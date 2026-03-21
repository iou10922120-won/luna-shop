-- ============================================================
-- 퍼널 분석 (Funnel Analysis)
-- ============================================================
-- 세션 기반 구매 퍼널: 방문 → 상품 조회 → 장바구니 → 결제 시작 → 구매 완료
-- 일별 단계별 유니크 세션 수 + 전환율
-- Tableau: 날짜 필터 + 퍼널 차트 또는 라인 차트로 시각화
-- ============================================================

WITH funnel_steps AS (
    SELECT
        created_at::date AS date,
        session_id,
        MAX(CASE WHEN event_name = 'session_start' THEN 1 ELSE 0 END) AS step_visit,
        MAX(CASE WHEN event_name = 'product_view' THEN 1 ELSE 0 END) AS step_product_view,
        MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS step_add_to_cart,
        MAX(CASE WHEN event_name = 'checkout_start' THEN 1 ELSE 0 END) AS step_checkout,
        MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS step_purchase
    FROM sessions
    GROUP BY created_at::date, session_id
)
SELECT
    date AS "날짜",
    SUM(step_visit) AS "방문",
    SUM(step_product_view) AS "상품조회",
    SUM(step_add_to_cart) AS "장바구니",
    SUM(step_checkout) AS "결제시작",
    SUM(step_purchase) AS "구매완료",
    -- 단계별 전환율
    ROUND(SUM(step_product_view)::numeric / NULLIF(SUM(step_visit), 0) * 100, 1) AS "조회전환율(%)",
    ROUND(SUM(step_add_to_cart)::numeric / NULLIF(SUM(step_product_view), 0) * 100, 1) AS "장바구니전환율(%)",
    ROUND(SUM(step_checkout)::numeric / NULLIF(SUM(step_add_to_cart), 0) * 100, 1) AS "결제전환율(%)",
    ROUND(SUM(step_purchase)::numeric / NULLIF(SUM(step_checkout), 0) * 100, 1) AS "구매전환율(%)",
    -- 전체 전환율 (방문 → 구매)
    ROUND(SUM(step_purchase)::numeric / NULLIF(SUM(step_visit), 0) * 100, 1) AS "전체전환율(%)"
FROM funnel_steps
GROUP BY date
ORDER BY date;
