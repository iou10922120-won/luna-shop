# LUNA — 비건 스킨케어 D2C 쇼핑몰

> "달빛처럼, 투명하게."

포트폴리오 목적의 비건 화장품 D2C 쇼핑몰 프로젝트입니다.
브랜드 기획 → 웹 앱 개발 → 데이터 분석 → 마케팅 전략까지 커머스의 전체 사이클을 직접 설계하고 구현했습니다.

**프로젝트 기간**: 2026.03.20 ~ 2026.03.21

---

## 링크

- [Live Demo](https://luna-shop.vercel.app) — Vercel 배포
- [분석 인사이트 리포트](prd/reports/final-insights.md) — 최종 분석 결과
- [포트폴리오 발표 자료](prd/reports/portfolio-deck.md) — 프로젝트 요약 덱

---

## 프로젝트 구조

```
luna-shop/
├── CLAUDE.md                    # 프로젝트 전체 컨텍스트
├── README.md                    # 이 파일
│
├── prd/                         # 기획 문서
│   ├── roadmap.md               # 전체 개발 로드맵
│   ├── prd-main.md              # 기능 명세 / 이벤트 설계 / KPI
│   ├── agent/                   # 에이전트별 역할 정의
│   ├── strategy/                # 시장분석, 경쟁사, 포지셔닝, BM
│   │   ├── market-analysis.md
│   │   ├── competitive-analysis.md
│   │   ├── brand-positioning.md
│   │   └── business-model.md
│   ├── marketing/               # 마케팅 전략 산출물
│   │   ├── personas.md          # 3종 페르소나
│   │   ├── campaign-plan.md     # 4개 캠페인 기획
│   │   ├── copy-bank.md         # 카피라이팅 자산
│   │   └── insight-report.md   # 마케팅 인사이트 리포트
│   └── reports/                 # 최종 보고
│       ├── data-insights.md     # 데이터 분석 인사이트
│       ├── final-insights.md    # 최종 종합 인사이트
│       └── portfolio-deck.md    # 포트폴리오 발표 자료
│
├── web/                         # Next.js 쇼핑몰
│   ├── app/                     # App Router 페이지 (7개)
│   ├── components/              # 공통 컴포넌트
│   ├── src/
│   │   └── lib/
│   │       └── analytics/       # GTM + Amplitude + Mixpanel 추상화
│   └── ...
│
└── data/
    ├── csv/                     # 목업 데이터 8종 (CSV)
    │   ├── users.csv            # 1,000명 유저
    │   ├── products.csv         # 50개 SKU
    │   ├── orders.csv           # 2,850건 주문
    │   ├── order_items.csv      # 주문 상품 상세
    │   ├── sessions.csv         # 세션 로그
    │   ├── inventory.csv        # 재고 변동
    │   ├── reviews.csv          # 500건 리뷰
    │   └── categories.csv       # 카테고리
    ├── scripts/                 # Python 스크립트
    │   ├── generate_data.py     # 목업 데이터 생성
    │   ├── load_to_supabase.py  # Supabase 업로드
    │   ├── rfm_analysis.py      # RFM 세그먼테이션
    │   └── cohort_analysis.py   # 코호트 리텐션 분석
    ├── queries/                 # SQL 분석 쿼리 (5종)
    │   ├── 01_funnel_analysis.sql
    │   ├── 02_rfm_analysis.sql
    │   ├── 03_cohort_retention.sql
    │   ├── 04_inventory_turnover.sql
    │   └── 05_revenue_analysis.sql
    └── output/                  # 분석 결과 CSV
        ├── rfm_customers.csv
        ├── rfm_segment_summary.csv
        ├── cohort_retention_long.csv
        └── cohort_retention_pivot.csv
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Next.js 16 (App Router), React 19, Tailwind CSS, shadcn/ui |
| State | Zustand |
| Backend | Supabase (PostgreSQL, Auth, Storage) |
| Analytics | GTM, Amplitude, Mixpanel |
| Data | Python (pandas, matplotlib), SQL (PostgreSQL), Tableau |
| Deploy | Vercel |

---

## 주요 분석

### RFM 세그먼테이션

969명의 구매 고객을 Recency·Frequency·Monetary 기준으로 6개 세그먼트로 분류했습니다.

| 세그먼트 | 고객수 | 비율 | 평균 구매액 | 평균 구매 횟수 | 핵심 전략 |
|---------|--------|------|-----------|-------------|----------|
| VIP | 81명 | 8.4% | 99만원 | 13회 | 멤버십 혜택, 추천인 프로그램 |
| 충성고객 | 113명 | 11.7% | 36만원 | 5회 | VIP 전환 유도, 번들 추천 |
| 신규유망 | 316명 | 32.6% | 13만원 | 2회 | 2회차 쿠폰, 웰컴 시리즈 |
| 일반 | 153명 | 15.8% | 11만원 | 2회 | 구매 주기 리마인드 |
| 슬리퍼 | 293명 | 30.2% | 11만원 | 1회 | 카카오 친구톡 리타겟팅 |
| 이탈위험 | 13명 | 1.3% | 33만원 | 5회 | 개인화 이메일, 대폭 할인 |

### 코호트 리텐션

- **M0 구매율**: 초기 코호트(2025-04) 12.5% → 최근 코호트(2026-03) 95.7%로 크게 개선
- **핵심 발견**: 3회 이상 구매한 고객은 장기 리텐션(M6+) 20~35%에서 안정화
- **핵심 레버**: 가입 후 첫 30일 내 2회차 구매 유도(M0→M1 전환)가 장기 고객 전환의 분기점

### 구매 퍼널

| 단계 | 이벤트 | 전환율 |
|------|--------|--------|
| 1. 방문 | page_view | 100% |
| 2. 제품 조회 | product_view | 약 65% |
| 3. 장바구니 추가 | add_to_cart | 약 38% |
| 4. 결제 시작 | begin_checkout | 약 22% |
| 5. 구매 완료 | purchase | 약 15% |

최대 이탈 포인트: 제품 조회 → 장바구니 구간 (27%p 이탈)

---

## 산출물

| Phase | 산출물 | 설명 |
|-------|--------|------|
| 1: 브랜드 전략 | `prd/strategy/` | 시장분석, 경쟁사, 포지셔닝, BM |
| 2: 기능 기획 | `prd/prd-main.md` | PRD, 이벤트 설계, KPI |
| 3: 목업 데이터 | `data/csv/` | 목업 데이터 8종 (CSV) |
| 4: 웹 앱 | `web/` | Next.js 16 쇼핑몰 7페이지 |
| 5: 분석 연동 | `web/src/lib/analytics/` | GTM + Amplitude + Mixpanel 이벤트 추적 |
| 6: 데이터 분석 | `data/queries/`, `data/scripts/` | SQL 5종, Python 스크립트 2종 |
| 7: 마케팅 전략 | `prd/marketing/` | 캠페인 4종, 카피라이팅, 콘텐츠 캘린더 |
| 8: 최종 보고 | `prd/reports/` | 포트폴리오 덱, 종합 인사이트 |

---

## 로컬 실행

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/luna-shop.git
cd luna-shop

# 2. 웹 앱 실행
cd web
cp .env.example .env.local   # Supabase 키 설정
npm install
npm run dev
# http://localhost:3000 에서 확인
```

### 환경변수 설정 (`.env.local`)

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 데이터 분석 실행

```bash
cd data/scripts
pip install -r requirements.txt
python rfm_analysis.py        # RFM 세그먼테이션 → data/output/
python cohort_analysis.py     # 코호트 리텐션 → data/output/
```

---

## 핵심 인사이트 요약

1. **VIP 8.4%가 매출의 핵심**: 파레토 법칙 적용 — 상위 고객 유지가 최우선 방어 과제
2. **슬리퍼 30.2%가 최대 성장 기회**: 재활성화 시 CAC 없이 매출 증대 가능
3. **첫 30일이 고객의 생애를 결정**: M0→M1 전환율 개선이 리텐션 핵심 레버

---

## 만든 사람

이 프로젝트에 대해 궁금한 점이 있으시면 연락해 주세요.

---

*이 프로젝트는 포트폴리오 목적으로 제작되었습니다. 실제 상품 판매는 이루어지지 않습니다.*
