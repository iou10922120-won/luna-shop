-- ============================================================
-- 매출 분석 (Revenue Analysis)
-- ============================================================
-- 월별, 카테고리별, 채널별 매출 분석
-- Tableau: 월별 라인차트 + 카테고리 스택바 + 채널 파이차트
-- ============================================================

-- [쿼리 1] 월별 매출 추이
SELECT
    TO_CHAR(DATE_TRUNC('month', o.ordered_at), 'YYYY-MM') AS "월",
    COUNT(DISTINCT o.id) AS "주문수",
    COUNT(DISTINCT o.user_id) AS "구매자수",
    SUM(o.total_amount) AS "총매출(GMV)",
    SUM(o.discount_amount) AS "할인액",
    SUM(o.total_amount - o.discount_amount) AS "순매출",
    ROUND(AVG(o.total_amount)) AS "평균주문금액(AOV)",
    -- 신규 vs 재구매
    COUNT(DISTINCT o.user_id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM orders prev
            WHERE prev.user_id = o.user_id
              AND prev.ordered_at < DATE_TRUNC('month', o.ordered_at)
              AND prev.status NOT IN ('cancelled')
        )
    ) AS "신규구매자",
    COUNT(DISTINCT o.user_id) - COUNT(DISTINCT o.user_id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM orders prev
            WHERE prev.user_id = o.user_id
              AND prev.ordered_at < DATE_TRUNC('month', o.ordered_at)
              AND prev.status NOT IN ('cancelled')
        )
    ) AS "재구매자"
FROM orders o
WHERE o.status NOT IN ('cancelled')
GROUP BY DATE_TRUNC('month', o.ordered_at)
ORDER BY "월";

-- [쿼리 2] 카테고리별 매출
-- (Tableau에서 별도 시트로 사용하려면 이 쿼리만 따로 실행)
/*
SELECT
    c.name AS "카테고리",
    TO_CHAR(DATE_TRUNC('month', o.ordered_at), 'YYYY-MM') AS "월",
    SUM(oi.subtotal) AS "매출",
    SUM(oi.quantity) AS "판매수량",
    COUNT(DISTINCT o.id) AS "주문수",
    ROUND(AVG(oi.unit_price)) AS "평균단가"
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
JOIN categories c ON c.id = p.category_id
WHERE o.status NOT IN ('cancelled')
GROUP BY c.name, DATE_TRUNC('month', o.ordered_at)
ORDER BY "월", "매출" DESC;
*/

-- [쿼리 3] 채널별 매출 성과 (UTM 기반)
-- (Tableau에서 별도 시트로 사용하려면 이 쿼리만 따로 실행)
/*
SELECT
    COALESCE(o.utm_source, '(direct)') AS "유입채널",
    COALESCE(o.utm_medium, '(none)') AS "유입매체",
    COALESCE(o.utm_campaign, '(none)') AS "캠페인",
    COUNT(DISTINCT o.id) AS "주문수",
    COUNT(DISTINCT o.user_id) AS "구매자수",
    SUM(o.total_amount) AS "매출",
    ROUND(AVG(o.total_amount)) AS "AOV",
    -- 쿠폰 사용률
    ROUND(COUNT(o.coupon_code)::numeric / COUNT(*) * 100, 1) AS "쿠폰사용률(%)"
FROM orders o
WHERE o.status NOT IN ('cancelled')
GROUP BY o.utm_source, o.utm_medium, o.utm_campaign
ORDER BY "매출" DESC;
*/
