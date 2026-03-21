-- ============================================================
-- RFM 세그먼테이션 (RFM Segmentation)
-- ============================================================
-- 고객별 Recency(최근성), Frequency(빈도), Monetary(금액) 점수 산출
-- 6개 세그먼트로 분류: VIP / 충성고객 / 신규유망 / 이탈위험 / 슬리퍼 / 할인사냥꾼
-- Tableau: 세그먼트별 고객 수 파이차트 + 산점도(R vs F, 색상=M)
-- ============================================================

WITH rfm_raw AS (
    SELECT
        u.id AS user_id,
        u.name AS "고객명",
        u.email,
        u.signup_channel AS "가입채널",
        MAX(o.ordered_at::date) AS last_purchase_date,
        (CURRENT_DATE - MAX(o.ordered_at::date)) AS recency_days,
        COUNT(DISTINCT o.id) AS frequency,
        SUM(o.total_amount) AS monetary
    FROM users u
    JOIN orders o ON o.user_id = u.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY u.id, u.name, u.email, u.signup_channel
),
rfm_scored AS (
    SELECT
        *,
        CASE
            WHEN recency_days <= 14 THEN 5
            WHEN recency_days <= 30 THEN 4
            WHEN recency_days <= 60 THEN 3
            WHEN recency_days <= 90 THEN 2
            ELSE 1
        END AS r_score,
        CASE
            WHEN frequency >= 10 THEN 5
            WHEN frequency >= 7 THEN 4
            WHEN frequency >= 4 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END AS f_score,
        CASE
            WHEN monetary >= 500000 THEN 5
            WHEN monetary >= 300000 THEN 4
            WHEN monetary >= 150000 THEN 3
            WHEN monetary >= 50000 THEN 2
            ELSE 1
        END AS m_score
    FROM rfm_raw
)
SELECT
    user_id,
    "고객명",
    email,
    "가입채널",
    last_purchase_date AS "최근구매일",
    recency_days AS "경과일수",
    frequency AS "구매횟수",
    monetary AS "총구매액",
    r_score AS "R점수",
    f_score AS "F점수",
    m_score AS "M점수",
    (r_score + f_score + m_score) AS "RFM합계",
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP'
        WHEN r_score >= 3 AND f_score >= 3 THEN '충성고객'
        WHEN r_score >= 4 AND f_score <= 2 THEN '신규유망'
        WHEN r_score <= 2 AND f_score >= 3 THEN '이탈위험'
        WHEN r_score <= 2 AND f_score <= 2 THEN '슬리퍼'
        WHEN m_score <= 2 AND f_score >= 3 THEN '할인사냥꾼'
        ELSE '일반'
    END AS "세그먼트"
FROM rfm_scored
ORDER BY monetary DESC;
