-- ============================================================
-- 재고 회전율 분석 (Inventory Turnover Analysis)
-- ============================================================
-- 상품별 판매량, 현재 재고, 회전율, 예상 소진일
-- Tableau: 카테고리별 바차트 + 품절 위험 상품 하이라이트
-- ============================================================

WITH product_sales AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS total_sold,
        SUM(oi.subtotal) AS total_revenue,
        -- 월평균 판매량 (데이터 기간 기준)
        ROUND(
            SUM(oi.quantity)::numeric /
            GREATEST(
                EXTRACT(EPOCH FROM (MAX(o.ordered_at) - MIN(o.ordered_at))) / (30.0 * 86400),
                1
            ),
            1
        ) AS monthly_avg_sold
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY oi.product_id
),
current_stock AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        quantity_after AS current_stock
    FROM inventory
    ORDER BY product_id, created_at DESC
),
initial_stock AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        quantity_after AS initial_stock
    FROM inventory
    WHERE change_type = 'inbound'
    ORDER BY product_id, created_at ASC
)
SELECT
    p.name AS "상품명",
    c.name AS "카테고리",
    COALESCE(ist.initial_stock, p.stock_quantity) AS "초기재고",
    COALESCE(cs.current_stock, p.stock_quantity) AS "현재재고",
    COALESCE(ps.total_sold, 0) AS "총판매량",
    COALESCE(ps.total_revenue, 0) AS "총매출",
    COALESCE(ps.monthly_avg_sold, 0) AS "월평균판매",
    -- 재고 회전율 = 판매량 / 평균재고
    CASE
        WHEN COALESCE(cs.current_stock, p.stock_quantity) > 0
        THEN ROUND(COALESCE(ps.total_sold, 0)::numeric / COALESCE(cs.current_stock, p.stock_quantity), 2)
        ELSE 0
    END AS "재고회전율",
    -- 예상 소진일 = 현재재고 / 월평균판매 * 30
    CASE
        WHEN COALESCE(ps.monthly_avg_sold, 0) > 0
        THEN ROUND(COALESCE(cs.current_stock, p.stock_quantity)::numeric / ps.monthly_avg_sold * 30, 0)
        ELSE NULL
    END AS "예상소진일(일)",
    -- 재고 상태
    CASE
        WHEN COALESCE(cs.current_stock, p.stock_quantity) <= 0 THEN '품절'
        WHEN COALESCE(ps.monthly_avg_sold, 0) > 0
             AND COALESCE(cs.current_stock, p.stock_quantity)::numeric / ps.monthly_avg_sold * 30 <= 30 THEN '주의'
        ELSE '정상'
    END AS "재고상태"
FROM products p
LEFT JOIN categories c ON c.id = p.category_id
LEFT JOIN product_sales ps ON ps.product_id = p.id
LEFT JOIN current_stock cs ON cs.product_id = p.id
LEFT JOIN initial_stock ist ON ist.product_id = p.id
ORDER BY COALESCE(ps.total_sold, 0) DESC;
