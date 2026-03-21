# LUNA Shop — 데이터 분석 인사이트 리포트

> Phase 6 산출물
> 분석 기간: 2025년 4월 ~ 2026년 3월 (12개월)
> 분석 대상: 1,000명 유저, 2,850건 주문, 50개 SKU

---

## 1. 핵심 KPI 요약

| 지표 | 값 | 해석 |
|------|-----|------|
| 총 구매 고객 | 969명 (전체 1,000명 중 96.9%) | 높은 구매 전환율 |
| 총 주문 수 | 2,850건 | 인당 평균 2.9회 구매 |
| VIP 고객 비율 | 8.4% (81명) | 파레토 법칙 적용 가능 |
| 재구매 고객 | ~69.8% (VIP+충성+이탈위험+일반 중 2회+) | 건강한 재구매 지표 |
| 슬리퍼 비율 | 30.2% (293명) | 1회 구매 후 이탈 — 리타겟팅 필요 |

---

## 2. RFM 세그먼테이션 인사이트

### 세그먼트 분포

전체 969명의 구매 고객을 6개 세그먼트로 분류:

| 세그먼트 | 고객수 | 비율 | 평균 구매액 | 평균 구매 횟수 | 핵심 특성 |
|---------|--------|------|-----------|-------------|----------|
| **VIP** | 81명 | 8.4% | 99만원 | 13회 | 최근 구매(9일), 고빈도, 고금액 |
| **충성고객** | 113명 | 11.7% | 36만원 | 5회 | 꾸준한 구매, VIP 전환 후보 |
| **신규유망** | 316명 | 32.6% | 13만원 | 2회 | 최근 가입, 빈도 확대 필요 |
| **일반** | 153명 | 15.8% | 11만원 | 2회 | 관심은 있으나 습관화 안 됨 |
| **슬리퍼** | 293명 | 30.2% | 11만원 | 1회 | 1회 구매 후 장기 미구매 (114일) |
| **이탈위험** | 13명 | 1.3% | 33만원 | 5회 | 과거 충성 고객, 최근 96일 미구매 |

### 액션 포인트

1. **VIP 유지 (81명)**: 전용 혜택(얼리액세스, 한정판), 추천인 프로그램으로 자연 유입 확대
2. **충성 → VIP 전환 (113명)**: 구매 횟수 7회 이상 시 VIP 승급, 번들 상품 추천으로 AOV 상승
3. **신규유망 활성화 (316명)**: 2회차 구매 쿠폰(10~15%), 리뷰 작성 인센티브
4. **슬리퍼 리타겟팅 (293명)**: 카카오 친구톡 재방문 캠페인, "다시 만나요" 할인 쿠폰
5. **이탈위험 긴급 대응 (13명)**: 고가치 고객이므로 개인화 이메일 + 큰 폭 할인으로 회복 시도

---

## 3. 코호트 리텐션 인사이트

### 리텐션 패턴

- **M0 (가입 월 구매율)**: 초기 코호트(2025-04) 12.5% → 최근 코호트(2026-03) 95.7%로 **크게 개선**
- **M1 리텐션**: 16~76%로 코호트별 편차 큼
- **장기 리텐션 (M6+)**: 20~35% 수준에서 안정화 — 핵심 고객 풀이 형성됨
- **2025-12~2026-02 코호트**: M0~M2 모두 높은 리텐션 → 마케팅 개선 효과 또는 계절적 요인

### 액션 포인트

1. **M0→M1 전환이 핵심**: 가입 후 첫 달 내 2회차 구매 유도 (웰컴 시리즈 자동화)
2. **M3 이후 안정화 구간 진입**: 3회 이상 구매 고객은 장기 유지 가능성 높음 → 3회차 구매 집중
3. **최근 코호트 품질 모니터링**: 2026-01~03 코호트의 높은 M0가 자연 전환인지 프로모션 효과인지 추적 필요

---

## 4. Tableau 대시보드 가이드

### 추천 시트 구성 (4개)

| 시트 | 데이터 소스 | 시각화 유형 | 핵심 질문 |
|------|-----------|-----------|----------|
| **매출 트렌드** | `05_revenue_analysis.sql` 또는 `daily_sales_summary` 테이블 | 라인 차트 (월별) + KPI 카드 | 매출이 성장하고 있는가? |
| **구매 퍼널** | `01_funnel_analysis.sql` 또는 `funnel_daily` 테이블 | 퍼널 바 차트 + 전환율 라인 | 어디서 이탈하는가? |
| **고객 세그먼트** | `rfm_segment_summary.csv` 또는 `rfm_segments` 테이블 | 파이 차트 + 산점도(R vs F) | 고객 구성은 건강한가? |
| **코호트 리텐션** | `cohort_retention_pivot.csv` 또는 `monthly_cohort` 테이블 | 히트맵 (코호트 × 월) | 리텐션이 개선되고 있는가? |

### Tableau 데이터 연결 방법

**방법 A: CSV 직접 임포트**
- `data/output/rfm_customers.csv`
- `data/output/rfm_segment_summary.csv`
- `data/output/cohort_retention_long.csv`
- `data/csv/orders.csv` + `order_items.csv` + `products.csv` (조인)

**방법 B: Supabase PostgreSQL 직접 연결**
- 서버: Supabase 프로젝트 URL의 DB host
- 포트: 5432
- 데이터베이스: postgres
- 요약 테이블 사용: `daily_sales_summary`, `funnel_daily`, `rfm_segments`, `monthly_cohort`, `product_performance`

---

## 5. 분석 산출물 정리

| 파일 | 설명 | 용도 |
|------|------|------|
| `data/queries/01_funnel_analysis.sql` | 퍼널 분석 쿼리 | Supabase/Tableau |
| `data/queries/02_rfm_analysis.sql` | RFM 세그먼테이션 쿼리 | Supabase/Tableau |
| `data/queries/03_cohort_retention.sql` | 코호트 리텐션 쿼리 | Supabase/Tableau |
| `data/queries/04_inventory_turnover.sql` | 재고 회전율 쿼리 | Supabase/Tableau |
| `data/queries/05_revenue_analysis.sql` | 매출 분석 쿼리 | Supabase/Tableau |
| `data/scripts/rfm_analysis.py` | RFM Python 분석 | CSV 출력 |
| `data/scripts/cohort_analysis.py` | 코호트 Python 분석 | CSV 출력 |
| `data/output/rfm_customers.csv` | 고객별 RFM 상세 | Tableau 임포트 |
| `data/output/rfm_segment_summary.csv` | 세그먼트 요약 | Tableau 임포트 |
| `data/output/cohort_retention_long.csv` | 코호트 리텐션 (long) | Tableau 임포트 |
| `data/output/cohort_retention_pivot.csv` | 코호트 리텐션 (pivot) | 확인용 |
