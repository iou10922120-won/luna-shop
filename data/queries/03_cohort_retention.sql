-- ============================================================
-- 코호트 리텐션 분석 (Cohort Retention Analysis)
-- ============================================================
-- 가입 월 기준 코호트별 월간 구매 리텐션율
-- Tableau: 히트맵(코호트 월 × 오프셋 월, 값=리텐션율)
-- ============================================================

WITH user_cohorts AS (
    SELECT
        id AS user_id,
        DATE_TRUNC('month', created_at)::date AS cohort_month
    FROM users
),
user_orders AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', ordered_at)::date AS order_month
    FROM orders
    WHERE status NOT IN ('cancelled')
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_size
    FROM user_cohorts
    GROUP BY cohort_month
),
retention_data AS (
    SELECT
        uc.cohort_month,
        (EXTRACT(YEAR FROM uo.order_month) - EXTRACT(YEAR FROM uc.cohort_month)) * 12
            + (EXTRACT(MONTH FROM uo.order_month) - EXTRACT(MONTH FROM uc.cohort_month)) AS month_offset,
        COUNT(DISTINCT uc.user_id) AS retained_users
    FROM user_cohorts uc
    JOIN user_orders uo ON uc.user_id = uo.user_id
    GROUP BY uc.cohort_month, month_offset
)
SELECT
    TO_CHAR(rd.cohort_month, 'YYYY-MM') AS "코호트",
    cs.cohort_size AS "코호트크기",
    rd.month_offset AS "경과월수",
    rd.retained_users AS "잔존유저",
    ROUND(rd.retained_users::numeric / cs.cohort_size * 100, 1) AS "리텐션율(%)"
FROM retention_data rd
JOIN cohort_sizes cs ON cs.cohort_month = rd.cohort_month
WHERE rd.month_offset >= 0
ORDER BY rd.cohort_month, rd.month_offset;
