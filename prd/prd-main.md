# LUNA 쇼핑몰 PRD (Product Requirements Document)

> Phase 2: 기능 기획
> 작성일: 2026-03-20
> 목적: 포트폴리오용 MVP — 커머스 데이터 분석 역량 증명

---

## 1. 정보 구조 (Information Architecture)

### 사이트맵

```
LUNA (luna-shop.vercel.app)
│
├── / (홈)
│   ├── 히어로 배너
│   ├── 베스트셀러 4종
│   ├── 브랜드 스토리 섹션
│   └── 성분 투명성 소개
│
├── /products (제품 목록)
│   ├── 카테고리 필터 (클렌저/토너/세럼/크림/선크림)
│   ├── 정렬 (인기순/가격순/신상품순/리뷰순)
│   └── 페이지네이션
│
├── /products/[id] (제품 상세)
│   ├── 제품 이미지
│   ├── 가격·옵션
│   ├── 성분 정보 (투명성 카드)
│   ├── 리뷰
│   └── 장바구니 추가
│
├── /cart (장바구니)
│   ├── 상품 목록·수량 조정
│   ├── 쿠폰 적용
│   └── 주문 요약
│
├── /checkout (결제)
│   ├── 배송지 입력
│   ├── 결제 수단 선택 (모킹)
│   └── 최종 주문 확인
│
├── /order/complete (주문 완료)
│   ├── 주문 번호
│   └── 예상 배송일
│
├── /mypage (마이페이지)
│   ├── 주문 내역
│   ├── 적립금
│   └── 리뷰 관리
│
└── /auth (인증)
    ├── 로그인 (소셜: Google, Kakao)
    └── 회원가입
```

### 글로벌 네비게이션

```
┌─────────────────────────────────────────────────────────┐
│  [LUNA 로고]   전체상품   베스트   브랜드소개   [검색] [장바구니] [마이] │
└─────────────────────────────────────────────────────────┘
```

- 비로그인: 장바구니 아이콘 → 로그인 유도, 마이 → 로그인 페이지
- 로그인: 장바구니 배지(수량), 마이 → 마이페이지
- 모바일: 하단 탭 네비게이션 (홈/카테고리/검색/장바구니/마이)

---

## 2. 유저 플로우

### 플로우 1: 탐색 → 구매 (핵심 매출 퍼널)

```
홈 방문
  │
  ├─→ 베스트셀러 클릭 ──→ 제품 상세
  │                          │
  └─→ 전체상품 ──→ 카테고리 필터 ──→ 제품 상세
                                       │
                                  장바구니 추가
                                       │
                                  장바구니 확인
                                       │
                                   결제 시작
                                       │
                              배송지 + 결제수단
                                       │
                                  결제 완료 ✓
                                       │
                                  주문완료 페이지
```

**측정 포인트 (퍼널 단계)**
| 단계 | 이벤트 | 예상 전환율 |
|------|--------|-----------|
| 방문 → 상품 조회 | `product_view` | 40~50% |
| 상품 조회 → 장바구니 | `add_to_cart` | 15~25% |
| 장바구니 → 결제 시작 | `checkout_start` | 50~65% |
| 결제 시작 → 결제 완료 | `purchase` | 70~85% |
| **전체 전환율** (방문→구매) | — | **2~5%** |

### 플로우 2: 가입 → 첫 구매

```
홈/제품 상세
  │
  └─→ 장바구니 추가 (비로그인)
         │
         └─→ 결제 시작 → 로그인 필요
                │
                ├─→ 소셜 로그인 (Google/Kakao)
                │         │
                └─→ 회원가입
                          │
                     결제 플로우 복귀
                          │
                     결제 완료 ✓
```

**측정 포인트**
- 회원가입 → 첫 구매 전환율 (당일/7일/30일)
- 가입 경로별 전환율 (Google vs Kakao)
- 가입 시점 (결제 직전 vs 자발적 가입)

### 플로우 3: 재방문 → 재구매

```
푸시/이메일/직접 방문
  │
  └─→ 홈 or 마이페이지
         │
         ├─→ 이전 주문 → "재주문" 클릭 → 장바구니 → 결제
         │
         └─→ 신제품/추천 탐색 → 제품 상세 → 장바구니 → 결제
```

**측정 포인트**
- 재방문 주기 (첫 구매 후 평균 며칠 만에 재방문)
- 재구매 전환율 (재방문자 중 구매 비율)
- 재구매 경로 (재주문 vs 신규 탐색)

---

## 3. DB 스키마

### 테이블 관계도

```
users ─────────┬──────────── orders ──────── order_items
  │            │                │                 │
  │            │                │                 │
  └── cart_items               └── (FK)          └── products
                                                      │
reviews ───── (FK: user_id, product_id)               │
                                                 categories
sessions ──── (FK: user_id)
                                                 inventory
                                                   │
                                              (FK: product_id)
```

### 테이블 상세

#### users (회원)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | Supabase Auth UID | 유저 식별 |
| email | text | 이메일 | — |
| name | text | 이름 | — |
| phone | text | 전화번호 | — |
| gender | text | 성별 | 세그먼트 분석 |
| birth_date | date | 생년월일 | 연령대별 분석 |
| signup_channel | text | 가입 경로 (google/kakao) | 채널별 전환율 |
| utm_source | text | 최초 유입 소스 | 마케팅 귀속 |
| utm_medium | text | 최초 유입 매체 | 마케팅 귀속 |
| utm_campaign | text | 최초 유입 캠페인 | 캠페인 ROI |
| created_at | timestamptz | 가입일 | 코호트 기준일 |
| updated_at | timestamptz | 수정일 | — |

#### products (상품)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | 상품 ID | 상품별 분석 |
| name | text | 상품명 | — |
| slug | text (unique) | URL용 슬러그 | — |
| description | text | 설명 | — |
| price | integer | 정가 (원) | 매출, AOV |
| sale_price | integer | null | 할인가 | 할인 효과 분석 |
| category_id | uuid (FK) | 카테고리 | 카테고리별 분석 |
| image_url | text | 대표 이미지 | — |
| ingredients | text[] | 전성분 목록 | 성분 관심도 분석 |
| is_vegan_certified | boolean | 비건 인증 여부 | — |
| stock_quantity | integer | 현재 재고 | 재고 분석 |
| created_at | timestamptz | 등록일 | 신제품 효과 분석 |

#### categories (카테고리)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | 카테고리 ID | — |
| name | text | 카테고리명 | 카테고리별 매출 |
| slug | text (unique) | URL용 슬러그 | — |
| display_order | integer | 정렬 순서 | — |

카테고리 목록: 클렌저, 토너, 세럼, 크림, 선크림

#### orders (주문)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | 주문 ID | — |
| user_id | uuid (FK → users) | 주문자 | RFM, 코호트 |
| order_number | text (unique) | 주문번호 (LUNA-YYYYMMDD-XXXX) | — |
| status | text | 상태 (pending/paid/shipped/delivered/cancelled) | 주문 상태 분석 |
| total_amount | integer | 총 결제 금액 | 매출(GMV) |
| discount_amount | integer | 할인 금액 | 할인 효과 |
| shipping_fee | integer | 배송비 | — |
| shipping_address | jsonb | 배송지 정보 | 지역별 분석 |
| coupon_code | text | null | 적용 쿠폰 | 쿠폰 효과 분석 |
| utm_source | text | 주문 시 유입 소스 | 매출 귀속 |
| utm_medium | text | 주문 시 유입 매체 | 매출 귀속 |
| utm_campaign | text | 주문 시 유입 캠페인 | 캠페인 ROI |
| ordered_at | timestamptz | 주문일시 | 시간대별 분석, RFM(R) |
| created_at | timestamptz | 생성일 | — |

#### order_items (주문 상품)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | — | — |
| order_id | uuid (FK → orders) | 주문 | — |
| product_id | uuid (FK → products) | 상품 | 상품별 판매량 |
| quantity | integer | 수량 | RFM(F), 재고 분석 |
| unit_price | integer | 단가 | RFM(M) |
| subtotal | integer | 소계 (단가 × 수량) | 매출 |

#### cart_items (장바구니)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | — | — |
| user_id | uuid (FK → users) | 유저 | — |
| product_id | uuid (FK → products) | 상품 | 장바구니 이탈 분석 |
| quantity | integer | 수량 | — |
| added_at | timestamptz | 추가 시점 | 장바구니 체류 시간 |

#### reviews (리뷰)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | — | — |
| user_id | uuid (FK → users) | 작성자 | 리뷰어 세그먼트 |
| product_id | uuid (FK → products) | 상품 | 상품별 평점 |
| rating | integer | 평점 (1~5) | 만족도 분석 |
| content | text | 리뷰 내용 | 감성 분석 (확장) |
| created_at | timestamptz | 작성일 | 리뷰 속도 분석 |

#### sessions (세션/이벤트 로그)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | — | — |
| session_id | text | 세션 식별자 | 세션 단위 분석 |
| user_id | uuid (FK → users) null | 유저 (비로그인 시 null) | 유저 행동 연결 |
| event_name | text | 이벤트명 | 퍼널, 행동 분석 |
| event_params | jsonb | 이벤트 속성 | 상세 분석 |
| page_path | text | 페이지 경로 | 페이지별 분석 |
| referrer | text | 유입 경로 | 트래픽 분석 |
| utm_source | text | UTM 소스 | 채널 귀속 |
| utm_medium | text | UTM 매체 | 채널 귀속 |
| utm_campaign | text | UTM 캠페인 | 캠페인 분석 |
| device_type | text | 디바이스 (mobile/desktop/tablet) | 디바이스별 전환율 |
| created_at | timestamptz | 이벤트 발생 시각 | 시간대 분석 |

#### inventory (재고 변동 이력)
| 컬럼 | 타입 | 설명 | 분석 용도 |
|------|------|------|----------|
| id | uuid (PK) | — | — |
| product_id | uuid (FK → products) | 상품 | SKU별 재고 분석 |
| change_type | text | 변동 유형 (inbound/sale/return/adjust) | 재고 흐름 |
| quantity_change | integer | 변동 수량 (+/-) | 재고 회전율 |
| quantity_after | integer | 변동 후 재고 | 재고 수준 추적 |
| reason | text | 사유 | — |
| created_at | timestamptz | 변동 시각 | 재고 추이 |

---

## 4. 분석 기준 정의

### 4-0. 추적 범위: 비로그인 vs 로그인

퍼널 분석은 **비로그인 포함 전체 방문자** 대상, 고객 분석(RFM/코호트/리텐션)은 **로그인 유저만** 가능합니다.
이는 실제 커머스에서도 동일한 구조입니다.

| 분석 항목 | 비로그인 | 로그인 | 식별 키 |
|----------|---------|--------|---------|
| 퍼널 전환율 | ✅ | ✅ | session_id (익명 포함) |
| 페이지별 트래픽/바운스 | ✅ | ✅ | session_id |
| 채널별 유입 분석 | ✅ | ✅ | session.utm_* |
| 장바구니 이탈 분석 | ✅ (로컬스토리지) | ✅ (DB) | session_id / user_id |
| RFM 세그먼테이션 | ❌ | ✅ | user_id + orders |
| 코호트 리텐션 | ❌ | ✅ | user_id + created_at |
| LTV / 재구매율 | ❌ | ✅ | user_id + orders |
| 개인화 추천 | ❌ | ✅ | user_id |

**비로그인 → 로그인 전환 시**: 로그인 시점에 세션의 anonymous_id와 user_id를 연결 (identity stitching). 로그인 이전 해당 세션의 행동은 user_id에 소급 귀속.

**목업 데이터 생성 시**: 전체 방문 세션 중 약 30~40%를 로그인 세션으로 설정 (실제 D2C 쇼핑몰 로그인율 참고).

### 4-1. 세션 (Session) 정의

| 항목 | 기준 | 근거 |
|------|------|------|
| **세션 타임아웃** | 30분 비활동 시 세션 종료 | GA4/Amplitude 업계 표준 |
| **자정 처리** | 자정(00:00) 넘기면 새 세션 | 일별 분석 정확도 확보 |
| **세션 시작** | 첫 페이지 로드 시 `session_start` 이벤트 발생 | — |
| **세션 종료** | 마지막 이벤트 후 30분 경과 (후처리 판정) | 실시간 종료 감지는 불안정 |
| **세션 ID 생성** | `{user_id or anonymous_id}_{timestamp}` | 유저-세션 매핑 |
| **신규 방문** | 해당 디바이스에서 첫 세션 | 쿠키/로컬스토리지 기반 |
| **재방문** | 이전 세션 존재 | — |

### 세션 속성

```
session_id          — 고유 식별자
user_id             — 로그인 유저 (null 허용)
started_at          — 세션 시작 시각
ended_at            — 세션 종료 시각 (후처리)
duration_seconds    — 세션 길이 (ended_at - started_at)
page_view_count     — 페이지뷰 수
event_count         — 총 이벤트 수
entry_page          — 진입 페이지
exit_page           — 이탈 페이지
utm_source          — 유입 소스
utm_medium          — 유입 매체
utm_campaign        — 유입 캠페인
device_type         — mobile / desktop / tablet
is_bounce           — 페이지뷰 1회 + 10초 미만 체류 시 바운스
has_purchase        — 이 세션에서 구매 발생 여부
```

### 4-2. 퍼널 (Funnel) 정의

#### 매출 퍼널 (Revenue Funnel) — 핵심

```
[Visit] → [Product View] → [Add to Cart] → [Checkout Start] → [Purchase]
 방문        상품 조회        장바구니 추가      결제 시작         결제 완료
```

- **매출 귀속**: `Purchase` 이벤트 발생 시 해당 세션의 `orders.total_amount`가 매출
- **퍼널 윈도우**: 단일 세션 내 (세션 내 전환만 측정) 또는 7일 윈도우 (크로스 세션)
- **퍼널 방식**: 순차 퍼널 (단계 순서 보장) — 장바구니 없이 바로 결제는 별도 집계
- **추적 범위**: 비로그인 포함 전체 방문자 (session_id 기반)

#### ⭐ 핵심 전환 단계: Product View → Add to Cart

전체 퍼널 중 **Product View → Add to Cart**를 가장 중요한 매출 레버로 설정합니다.

**이유:**
1. **이탈폭이 가장 큼** — 상품을 본 사람의 75~85%가 장바구니에 담지 않고 이탈. 다른 단계(Cart→Checkout 35~50%, Checkout→Purchase 15~30%)보다 개선 여지가 압도적으로 큼
2. **개선 가능한 요소가 이 단계에 집중** — 성분 정보 표시, 리뷰, 가격/할인, 제품 이미지 등 LUNA가 통제할 수 있는 UX/콘텐츠 변수가 이 전환에 영향
3. **복리 효과** — 이 단계 전환율 1%p 개선 시, 하위 퍼널(Cart→Checkout→Purchase)에 그대로 전파되어 매출 임팩트가 가장 큼
4. **포트폴리오 가치** — "이 단계의 전환율을 분석하고, 세그먼트별 차이를 발견하고, 개선안을 도출했다"는 스토리가 데이터 분석 역량을 가장 잘 보여줌

#### 단계별 벤치마크 및 설정 근거

| 단계 전환 | 벤치마크 | 설정 근거 | 목업 데이터 적용 |
|----------|---------|----------|----------------|
| Visit → Product View | 40~50% | Shopify 평균 제품조회율 35~55%. D2C 화장품은 탐색 목적 방문이 많고 상품 수가 적어(50개) 조회까지 도달이 쉬움 | 45% 기준 |
| **Product View → Add to Cart** | **15~25%** | **글로벌 이커머스 평균 ATC율 8~12% (Baymard Institute, 2024). 뷰티 카테고리는 15~20%로 높은 편. LUNA는 D2C(목적성 높은 방문자)이므로 상단 적용** | **20% 기준** |
| Add to Cart → Checkout | 50~65% | 장바구니 이탈률 글로벌 평균 69.8% (Baymard, 46개 연구 메타분석) → 전환 약 30%. D2C는 비교쇼핑이 적어 전환이 높은 편 | 55% 기준 |
| Checkout → Purchase | 70~85% | 결제 시작 후 완료율은 결제 UX에 크게 의존. 간편결제(카카오/네이버) 도입 시 70~85%. MVP는 결제 모킹이라 실패 없음 | 80% 기준 |
| **Visit → Purchase (전체)** | **2~5%** | **이커머스 평균 전환율 1.5~3% (Statista, 2024). D2C 뷰티 브랜드는 방문자 의도가 높아 2~5% (Shopify 뷰티 카테고리 벤치마크)** | **3% 기준** |

> **참고**: 위 벤치마크는 업계 평균 참고치이며, 목업 데이터 생성 시 이 비율을 기준으로 현실적인 데이터를 시뮬레이션합니다. 실제 서비스에서는 A/B 테스트와 실측 데이터로 보정이 필요합니다.

#### 이탈 포인트별 의미

| 이탈 구간 | 이탈률 | 의미 | 개선 방향 |
|----------|--------|------|----------|
| Visit → Product View | 50~60% | 홈/목록에서 관심 제품을 못 찾음 | 추천 개선, 카테고리 UX, 검색 |
| **Product View → Cart** | **75~85%** | **제품은 봤지만 구매 의향 부족 (⭐ 핵심 이탈)** | **성분 정보, 리뷰, 가격, CTA 최적화** |
| Cart → Checkout | 35~50% | 장바구니 담았지만 결제 망설임 | 장바구니 리마인더, 쿠폰, 무료배송 안내 |
| Checkout → Purchase | 15~30% | 결제 과정에서 이탈 | 결제 UX 간소화, 결제수단 다양화 |

#### 가입 퍼널 (Registration Funnel)

```
[Visit] → [Signup Start] → [Signup Complete] → [First Purchase]
 방문        가입 시작         가입 완료          첫 구매
```

- 가입 후 첫 구매까지의 기간 (Time to First Purchase) 측정
- 벤치마크: 가입 후 7일 내 첫 구매 전환율 15~25%

#### 인게이지먼트 퍼널 (매출 아님, 리텐션 지표)

```
[First Purchase] → [Return Visit] → [Second Purchase] → [Review Write]
 첫 구매             재방문              재구매              리뷰 작성
```

- 재구매까지 평균 기간, 리뷰 작성률 측정
- 리뷰 작성 유저의 재구매율이 높은지 분석

### 4-3. 매출 귀속 (Attribution)

| 항목 | 기준 | 설명 |
|------|------|------|
| **귀속 모델** | 라스트 터치 (Last Touch) | 결제 완료 세션의 UTM을 매출 귀속 채널로 사용 |
| **귀속 윈도우** | 30일 | 첫 방문 후 30일 내 구매 시 귀속 |
| **직접 방문 처리** | 이전 UTM 유지 | 직접 방문(utm 없음) 시 가장 최근 UTM 세션 귀속 |
| **복수 채널 처리** | 라스트 터치 우선 | 포트폴리오 MVP에서는 라스트 터치만 구현 |

#### 채널 분류

| utm_source | utm_medium | 채널명 |
|-----------|-----------|--------|
| google | cpc | Google Ads |
| google | organic | Google 검색 |
| instagram | social | 인스타그램 |
| naver | organic | 네이버 검색 |
| naver | blog | 네이버 블로그 |
| kakao | cpc | 카카오 광고 |
| kakao | friendtalk | 카카오 친구톡 |
| youtube | social | 유튜브 |
| (direct) | (none) | 직접 방문 |
| referral | referral | 기타 레퍼럴 |

### 4-4. 코호트 (Cohort) 기준

| 항목 | 기준 | 이유 |
|------|------|------|
| **코호트 그룹핑** | 가입월 (signup month) | 유저 획득 시점별 행동 차이 분석 |
| **리텐션 기준 행동** | 구매 (purchase) | 커머스에서 가장 의미 있는 리텐션 |
| **리텐션 주기** | 월 단위 (M0, M1, M2, ...) | 화장품 구매 주기 2~3개월 고려 |
| **M0 정의** | 가입한 달 | 가입과 첫 구매가 같은 달인 비율 확인 |
| **활성 유저 정의** | 해당 월에 1회 이상 구매 | 방문만으로는 커머스 활성 유저로 부족 |

#### 코호트 테이블 예시

```
         M0    M1    M2    M3    M4    M5    M6
2025-01  100%  32%   18%   15%   14%   13%   12%
2025-02  100%  28%   16%   14%   12%   11%
2025-03  100%  35%   20%   17%   15%
...
```

- M1 리텐션 30% 이상 → 건강한 비즈니스
- M1 리텐션 20% 미만 → 제품/서비스 개선 필요

### 4-5. RFM 기준

| 지표 | 정의 | 스코어링 (1~5) |
|------|------|---------------|
| **Recency (R)** | 마지막 구매로부터 경과 일수 | 5: 0~14일, 4: 15~30일, 3: 31~60일, 2: 61~90일, 1: 91일+ |
| **Frequency (F)** | 최근 12개월 구매 횟수 | 5: 10회+, 4: 7~9회, 3: 4~6회, 2: 2~3회, 1: 1회 |
| **Monetary (M)** | 최근 12개월 총 구매 금액 | 5: 50만+, 4: 30~50만, 3: 15~30만, 2: 5~15만, 1: 5만 미만 |

#### RFM 세그먼트

| 세그먼트 | R | F | M | 설명 | 전략 |
|---------|---|---|---|------|------|
| **VIP** | 4~5 | 4~5 | 4~5 | 최근+자주+많이 구매 | 전용 혜택, 리텐션 유지 |
| **충성 고객** | 3~5 | 3~5 | 3~5 | 꾸준히 구매 | 업셀링, 추천 프로그램 |
| **신규 유망** | 4~5 | 1~2 | 1~3 | 최근 가입, 구매 시작 | 2차 구매 유도, 온보딩 |
| **이탈 위험** | 1~2 | 3~5 | 3~5 | 과거 충성 고객, 최근 미구매 | 재활성화 캠페인 |
| **슬리퍼** | 1~2 | 1~2 | 1~2 | 오래 전 1~2회 구매 후 이탈 | 윈백 쿠폰 or 포기 |
| **할인 사냥꾼** | 2~3 | 2~3 | 1~2 | 할인 시만 구매, 객단가 낮음 | 할인 의존도 낮추기 |

---

## 5. 분석 이벤트 설계

### 이벤트 목록

| 이벤트명 | 트리거 | 카테고리 |
|---------|--------|---------|
| `session_start` | 세션 시작 (첫 페이지 로드) | 세션 |
| `page_view` | 모든 페이지 진입 | 세션 |
| `product_list_view` | 제품 목록 페이지 조회 | 탐색 |
| `product_list_filter` | 카테고리/정렬 필터 사용 | 탐색 |
| `product_view` | 제품 상세 페이지 진입 | 탐색 |
| `ingredient_view` | 성분 정보 탭/섹션 클릭 | 탐색 |
| `add_to_cart` | 장바구니 추가 | 전환 |
| `remove_from_cart` | 장바구니 삭제 | 전환 |
| `cart_view` | 장바구니 페이지 진입 | 전환 |
| `checkout_start` | 결제 시작 | 전환 |
| `purchase` | 결제 완료 | 전환 (매출) |
| `signup_start` | 회원가입 폼 진입 | 인증 |
| `signup_complete` | 회원가입 완료 | 인증 |
| `login` | 로그인 완료 | 인증 |
| `review_write` | 리뷰 작성 완료 | 인게이지먼트 |
| `coupon_apply` | 쿠폰 적용 | 전환 |

### 이벤트별 속성 (Properties)

#### product_view
```json
{
  "product_id": "uuid",
  "product_name": "비건 클렌징 젤",
  "category": "클렌저",
  "price": 22000,
  "sale_price": null,
  "position": 3
}
```

#### add_to_cart
```json
{
  "product_id": "uuid",
  "product_name": "비건 클렌징 젤",
  "category": "클렌저",
  "price": 22000,
  "quantity": 1,
  "cart_total": 22000,
  "cart_item_count": 1
}
```

#### purchase
```json
{
  "order_id": "uuid",
  "order_number": "LUNA-20260320-0001",
  "total_amount": 88000,
  "discount_amount": 5000,
  "shipping_fee": 0,
  "item_count": 3,
  "items": [
    {"product_id": "uuid", "category": "세럼", "quantity": 1, "price": 38000},
    {"product_id": "uuid", "category": "크림", "quantity": 1, "price": 42000}
  ],
  "coupon_code": "WELCOME10",
  "payment_method": "card"
}
```

---

## 6. 핵심 KPI 정의

### Tier 1: 비즈니스 핵심 지표

| KPI | 정의 | 산식 | 목표 (1년차) |
|-----|------|------|-------------|
| **GMV** | 총 거래액 | SUM(orders.total_amount) WHERE status != 'cancelled' | 월 1,000만 원 |
| **전환율 (CVR)** | 방문 → 구매 전환율 | 구매 세션 수 / 총 세션 수 × 100 | 2~3% |
| **AOV** | 평균 주문 금액 | GMV / 주문 건수 | 45,000원 |
| **MAU** | 월간 활성 유저 | 해당 월 1회 이상 방문 유니크 유저 | 5,000 |
| **재구매율** | 2회 이상 구매 비율 | 2회+ 구매 유저 / 전체 구매 유저 × 100 | 25% |

### Tier 2: 성장 지표

| KPI | 정의 | 산식 | 목표 |
|-----|------|------|------|
| **CAC** | 고객 획득 비용 | 마케팅 비용 / 신규 구매 유저 수 | < 20,000원 |
| **LTV** | 고객 생애 가치 (12개월) | AOV × 연간 구매 횟수 × 마진율 | > 50,000원 |
| **LTV/CAC** | 고객 가치 대비 획득 비용 | LTV / CAC | > 3.0 |
| **MoM Growth** | 월간 매출 성장률 | (이번 달 GMV - 지난 달) / 지난 달 × 100 | 15~20% |
| **M1 Retention** | 가입 1개월 후 구매 리텐션 | M1에 구매한 유저 / M0 가입 유저 | > 30% |

### Tier 3: 운영 지표

| KPI | 정의 | 산식 | 목표 |
|-----|------|------|------|
| **장바구니 이탈율** | 장바구니 추가 후 미구매 비율 | (Cart - Purchase) / Cart × 100 | < 60% |
| **평균 세션 시간** | 세션당 평균 체류 시간 | AVG(session.duration_seconds) | > 3분 |
| **바운스율** | 1페이지만 보고 이탈 | 바운스 세션 / 전체 세션 × 100 | < 40% |
| **리뷰 작성률** | 구매 후 리뷰 작성 비율 | 리뷰 작성 유저 / 구매 유저 × 100 | > 10% |
| **재고 회전율** | 재고가 얼마나 빨리 팔리는지 | 판매량 / 평균 재고 (월 기준) | 카테고리별 상이 |

---

## 7. 데이터-분석 연결 맵

모든 페이지 기능이 어떤 데이터를 만들고, 그 데이터가 어떤 분석에 쓰이는지 한눈에 보는 맵.

```
[페이지]          [이벤트]              [DB 테이블]          [분석 항목]
─────────────────────────────────────────────────────────────────────────
홈               session_start         sessions            트래픽 분석
                 page_view                                 채널별 유입 분석
                                                          바운스율

제품 목록         product_list_view     sessions            카테고리별 관심도
                 product_list_filter                       필터 사용 패턴

제품 상세         product_view          sessions            퍼널 (조회 단계)
                 ingredient_view                           성분 관심도 분석
                 add_to_cart           cart_items           퍼널 (장바구니 단계)

장바구니          cart_view             sessions            장바구니 이탈 분석
                 remove_from_cart      cart_items           이탈 상품 분석
                 coupon_apply                              쿠폰 효과 분석

결제              checkout_start        sessions            퍼널 (결제 시작)
                 purchase              orders              매출(GMV), AOV
                                       order_items         상품별 판매량
                                       inventory           재고 차감

주문 완료         (purchase 후속)        orders              주문 상태 추적

마이페이지         review_write          reviews             리뷰 분석, 만족도
                 (주문 조회)            orders              재구매 패턴

인증              signup_complete       users               가입 퍼널
                 login                 sessions            로그인 빈도
─────────────────────────────────────────────────────────────────────────

                    ↓ 종합 분석 ↓

[분석 항목]                    [사용 데이터]                [산출물]
─────────────────────────────────────────────────────────────────────────
퍼널 분석                      sessions (이벤트 시퀀스)      단계별 전환율, 이탈 포인트
RFM 세그먼테이션                orders, order_items          고객 세그먼트 6종
코호트 리텐션                   users.created_at + orders    월별 리텐션 곡선
매출 분석                      orders, order_items          월별·카테고리별·채널별 매출
재고 분석                      inventory, order_items       회전율, 품절 예측
채널 귀속                      sessions.utm_* + orders      채널별 ROI
장바구니 이탈                   cart_items vs orders         이탈 상품·시점·금액 분석
```

---

## 8. 페이지 목록

| 페이지 | 경로 | 상세 문서 |
|--------|------|----------|
| 홈 | `/` | [pages/home.md](pages/home.md) |
| 제품 목록 | `/products` | [pages/products.md](pages/products.md) |
| 제품 상세 | `/products/[id]` | [pages/product-detail.md](pages/product-detail.md) |
| 장바구니 | `/cart` | [pages/cart.md](pages/cart.md) |
| 결제 | `/checkout` | [pages/checkout.md](pages/checkout.md) |
| 주문 완료 | `/order/complete` | [pages/order-complete.md](pages/order-complete.md) |
| 마이페이지 | `/mypage` | [pages/mypage.md](pages/mypage.md) |
| 로그인/회원가입 | `/auth` | [pages/auth.md](pages/auth.md) |
