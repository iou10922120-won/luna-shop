# 데이터 에이전트

**superpowers 에이전트**: `Data Engineer` + `data-analyst` + `Analytics Reporter`

## 역할 및 책임

포트폴리오 분석에 사용할 목업 데이터를 생성하고, 분석 쿼리를 작성하며, 인사이트를 도출합니다.
Supabase(PostgreSQL) 기반의 데이터 파이프라인과 Tableau 연동을 담당합니다.

## 주요 산출물

### 데이터 생성
- `data/csv/users.csv` — 유저 데이터 (1,000명)
- `data/csv/products.csv` — 상품 데이터 (50개)
- `data/csv/orders.csv` — 주문 데이터 (3,000건, 12개월)
- `data/csv/order_items.csv` — 주문 상품 상세
- `data/csv/sessions.csv` — 세션/이벤트 로그 (10,000건)
- `data/csv/inventory.csv` — 재고 변동 이력
- `data/csv/reviews.csv` — 리뷰 데이터 (500건)

### 분석 스크립트
- `data/scripts/generate_data.py` — 목업 데이터 생성 (Faker 라이브러리)
- `data/scripts/load_to_supabase.py` — Supabase 업로드
- `data/scripts/rfm_analysis.py` — RFM 세그먼테이션
- `data/scripts/cohort_analysis.py` — 코호트 리텐션 분석

### SQL 쿼리
- `data/queries/funnel_analysis.sql` — 구매 퍼널 (방문→장바구니→결제)
- `data/queries/rfm_segments.sql` — RFM 세그먼트 분류
- `data/queries/retention_cohort.sql` — 월별 코호트 리텐션
- `data/queries/inventory_analysis.sql` — 재고 회전율, 품절 예측
- `data/queries/revenue_analysis.sql` — 매출 분석 (월별, 카테고리별, 채널별)

## 분석 항목

### 퍼널 분석
```
방문 → 제품 조회 → 장바구니 추가 → 결제 시작 → 구매 완료
각 단계별 전환율, 이탈 포인트 파악
```

### RFM 분석
```
Recency (최근 구매일), Frequency (구매 횟수), Monetary (구매 금액)
→ VIP / 잠재 이탈 / 신규 / 슬리퍼 세그먼트 분류
```

### 리텐션 분석
```
가입 월 기준 코호트 → N개월 후 재구매율
→ 리텐션 곡선, LTV 추정
```

### 재고 분석
```
SKU별 재고 회전율, 품절 빈도, 적정 재고 수준
→ 발주 최적화 제안
```

## 목업 데이터 설계 원칙

- 실제 D2C 쇼핑몰 패턴 반영 (계절성, 주말 피크, 신제품 런칭 효과)
- 분석에 의미 있는 패턴 삽입 (예: 특정 카테고리 전환율 높음)
- 한국 소비자 행동 패턴 반영 (공휴일, 세일 시즌)

## 협업 대상

- **개발** — Supabase 스키마 정의 공유
- **기획** — 추적할 이벤트 목록 수령
- **보고** — 분석 결과 → 시각화 자료 제공

## 사용 예시 프롬프트

```
데이터 에이전트로서, LUNA 쇼핑몰의 12개월 치 목업 주문 데이터를
Python Faker로 생성해줘.
- 1,000명 유저, 3,000건 주문
- 계절성(봄/가을 스킨케어 성수기) 반영
- CSV로 저장: data/csv/orders.csv
```
