-- ============================================================
-- LUNA Shop - 요약 테이블 빌드
-- ============================================================
-- CSV 데이터가 Supabase에 업로드된 후 실행
-- Supabase SQL Editor에서 전체 복사-붙여넣기 후 Run
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. daily_sales_summary (일별 매출 요약)
-- ────────────────────────────────────────────────────────────
TRUNCATE TABLE daily_sales_summary;

INSERT INTO daily_sales_summary (date, total_orders, total_revenue, total_items_sold, avg_order_value, unique_buyers)
SELECT
    o.ordered_at::date AS date,
    COUNT(DISTINCT o.id) AS total_orders,
    SUM(o.total_amount) AS total_revenue,
    SUM(oi.quantity) AS total_items_sold,
    AVG(o.total_amount)::integer AS avg_order_value,
    COUNT(DISTINCT o.user_id) AS unique_buyers
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status NOT IN ('cancelled')
GROUP BY o.ordered_at::date
ORDER BY date;

-- ────────────────────────────────────────────────────────────
-- 2. funnel_daily (일별 퍼널 단계별 세션 수)
-- ────────────────────────────────────────────────────────────
TRUNCATE TABLE funnel_daily;

INSERT INTO funnel_daily (date, step, session_count)
SELECT
    created_at::date AS date,
    event_name AS step,
    COUNT(DISTINCT session_id) AS session_count
FROM sessions
WHERE event_name IN ('session_start', 'product_view', 'add_to_cart', 'checkout_start', 'purchase')
GROUP BY created_at::date, event_name
ORDER BY date, step;

-- ────────────────────────────────────────────────────────────
-- 3. monthly_cohort (월별 코호트 리텐션)
-- ────────────────────────────────────────────────────────────
TRUNCATE TABLE monthly_cohort;

WITH user_cohorts AS (
    -- 유저별 가입 월 (코호트)
    SELECT
        id AS user_id,
        DATE_TRUNC('month', created_at)::date AS cohort_month
    FROM users
),
user_orders AS (
    -- 유저별 주문 월
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', ordered_at)::date AS order_month
    FROM orders
    WHERE status NOT IN ('cancelled')
),
cohort_sizes AS (
    -- 코호트별 가입자 수
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM user_cohorts
    GROUP BY cohort_month
),
retention_raw AS (
    -- 코호트 × 오프셋 조합별 잔존 유저 수
    SELECT
        uc.cohort_month,
        (EXTRACT(YEAR FROM uo.order_month) - EXTRACT(YEAR FROM uc.cohort_month)) * 12
            + (EXTRACT(MONTH FROM uo.order_month) - EXTRACT(MONTH FROM uc.cohort_month)) AS month_offset,
        COUNT(DISTINCT uc.user_id) AS retained_users
    FROM user_cohorts uc
    JOIN user_orders uo ON uc.user_id = uo.user_id
    GROUP BY uc.cohort_month, month_offset
)
INSERT INTO monthly_cohort (cohort_month, month_offset, cohort_size, retained_users, retention_rate)
SELECT
    rr.cohort_month,
    rr.month_offset::integer,
    cs.cohort_size,
    rr.retained_users,
    ROUND(rr.retained_users::numeric / cs.cohort_size * 100, 2) AS retention_rate
FROM retention_raw rr
JOIN cohort_sizes cs ON cs.cohort_month = rr.cohort_month
WHERE rr.month_offset >= 0
ORDER BY rr.cohort_month, rr.month_offset;

-- ────────────────────────────────────────────────────────────
-- 4. rfm_segments (유저별 RFM 세그먼트)
-- ────────────────────────────────────────────────────────────
TRUNCATE TABLE rfm_segments;

WITH rfm_raw AS (
    SELECT
        u.id AS user_id,
        MAX(o.ordered_at::date) AS last_purchase_date,
        (CURRENT_DATE - MAX(o.ordered_at::date)) AS recency_days,
        COUNT(DISTINCT o.id) AS frequency,
        SUM(o.total_amount) AS monetary
    FROM users u
    JOIN orders o ON o.user_id = u.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY u.id
),
rfm_scored AS (
    SELECT
        user_id,
        last_purchase_date,
        recency_days,
        frequency,
        monetary,
        -- R score: 최근 구매일 기준 (0-14일=5, 15-30=4, 31-60=3, 61-90=2, 91+=1)
        CASE
            WHEN recency_days <= 14 THEN 5
            WHEN recency_days <= 30 THEN 4
            WHEN recency_days <= 60 THEN 3
            WHEN recency_days <= 90 THEN 2
            ELSE 1
        END AS r_score,
        -- F score: 구매 빈도 (10+=5, 7-9=4, 4-6=3, 2-3=2, 1=1)
        CASE
            WHEN frequency >= 10 THEN 5
            WHEN frequency >= 7 THEN 4
            WHEN frequency >= 4 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END AS f_score,
        -- M score: 총 구매액 (50만+=5, 30-50만=4, 15-30만=3, 5-15만=2, 5만-=1)
        CASE
            WHEN monetary >= 500000 THEN 5
            WHEN monetary >= 300000 THEN 4
            WHEN monetary >= 150000 THEN 3
            WHEN monetary >= 50000 THEN 2
            ELSE 1
        END AS m_score
    FROM rfm_raw
)
INSERT INTO rfm_segments (user_id, last_purchase_date, recency_days, frequency, monetary, r_score, f_score, m_score, rfm_segment, calculated_at)
SELECT
    user_id,
    last_purchase_date,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    -- 세그먼트 분류
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP'
        WHEN r_score >= 3 AND f_score >= 3 THEN '충성고객'
        WHEN r_score >= 4 AND f_score <= 2 THEN '신규유망'
        WHEN r_score <= 2 AND f_score >= 3 THEN '이탈위험'
        WHEN r_score <= 2 AND f_score <= 2 THEN '슬리퍼'
        WHEN m_score <= 2 AND f_score >= 3 THEN '할인사냥꾼'
        ELSE '일반'
    END AS rfm_segment,
    NOW() AS calculated_at
FROM rfm_scored;

-- ────────────────────────────────────────────────────────────
-- 5. product_performance (상품별 성과)
-- ────────────────────────────────────────────────────────────
TRUNCATE TABLE product_performance;

WITH product_sales AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS total_sold,
        SUM(oi.subtotal) AS total_revenue
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY oi.product_id
),
product_reviews AS (
    SELECT
        product_id,
        AVG(rating)::numeric(3,2) AS avg_rating,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
),
product_stock AS (
    -- 각 상품의 최신 재고량
    SELECT DISTINCT ON (product_id)
        product_id,
        quantity_after AS current_stock
    FROM inventory
    ORDER BY product_id, created_at DESC
)
INSERT INTO product_performance (product_id, product_name, category, total_sold, total_revenue, avg_rating, review_count, current_stock, inventory_turnover, calculated_at)
SELECT
    p.id AS product_id,
    p.name AS product_name,
    c.name AS category,
    COALESCE(ps.total_sold, 0) AS total_sold,
    COALESCE(ps.total_revenue, 0) AS total_revenue,
    pr.avg_rating,
    COALESCE(pr.review_count, 0) AS review_count,
    COALESCE(pst.current_stock, p.stock_quantity) AS current_stock,
    -- 재고 회전율: 판매량 / 평균재고 (연간 기준, 간이 계산)
    CASE
        WHEN COALESCE(pst.current_stock, p.stock_quantity) > 0
        THEN ROUND(COALESCE(ps.total_sold, 0)::numeric / COALESCE(pst.current_stock, p.stock_quantity), 2)
        ELSE 0
    END AS inventory_turnover,
    NOW() AS calculated_at
FROM products p
LEFT JOIN categories c ON c.id = p.category_id
LEFT JOIN product_sales ps ON ps.product_id = p.id
LEFT JOIN product_reviews pr ON pr.product_id = p.id
LEFT JOIN product_stock pst ON pst.product_id = p.id;

-- ────────────────────────────────────────────────────────────
-- 완료 확인
-- ────────────────────────────────────────────────────────────
SELECT 'daily_sales_summary' AS table_name, COUNT(*) AS rows FROM daily_sales_summary
UNION ALL
SELECT 'funnel_daily', COUNT(*) FROM funnel_daily
UNION ALL
SELECT 'monthly_cohort', COUNT(*) FROM monthly_cohort
UNION ALL
SELECT 'rfm_segments', COUNT(*) FROM rfm_segments
UNION ALL
SELECT 'product_performance', COUNT(*) FROM product_performance;
