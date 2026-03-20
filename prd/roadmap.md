# LUNA Shop — 전체 개발 로드맵

> 포트폴리오용 비건 화장품 D2C 쇼핑몰
> 목표: 커머스 데이터 분석 + 마케팅/브랜드 전략 포트폴리오 완성

---

## 전체 구조

```
Phase 1: 브랜드 전략        [사업전략, 마케팅]
Phase 2: 기능 기획 / PRD    [PM, 기획]
Phase 3: 목업 데이터 생성   [데이터]
Phase 4: 웹 앱 개발         [개발]
Phase 5: 분석 도구 연동     [개발, 데이터]
Phase 6: 데이터 분석        [데이터]
Phase 7: 마케팅 전략        [마케팅]
Phase 8: 최종 보고          [보고]
```

---

## Phase 1 — 브랜드 전략 수립

**담당**: 사업전략 에이전트, 마케팅 에이전트
**목표**: LUNA 브랜드의 시장 포지셔닝과 타겟 페르소나 정의

### 작업 목록
- [ ] 국내 비건 화장품 시장 분석 (규모, 성장률, 트렌드)
- [ ] 경쟁사 분석 (이니스프리, 닥터자르트, 톤28, 아로마티카)
- [ ] LUNA 브랜드 포지셔닝 맵 작성
- [ ] 비즈니스 모델 캔버스 (BM Canvas)
- [ ] 타겟 페르소나 1차 정의 (3종)
- [ ] 브랜드 스토리 & 슬로건 초안

### 산출물
- `prd/strategy/market-analysis.md`
- `prd/strategy/competitive-analysis.md`
- `prd/strategy/brand-positioning.md`
- `prd/strategy/business-model.md`
- `prd/marketing/personas.md` (초안)

---

## Phase 2 — 기능 기획 / PRD

**담당**: PM 에이전트, 기획 에이전트
**목표**: 전체 기능 요구사항과 페이지별 PRD 작성

### 작업 목록
- [ ] 기능 요구사항 목록 (백로그) 작성
- [ ] 사이트맵 / 정보 구조(IA) 정의
- [ ] 유저 스토리 10개 이상 작성
- [ ] 페이지별 기능 명세 (홈, 목록, 상세, 장바구니, 결제, 마이페이지)
- [ ] 분석 이벤트 목록 정의 (GTM/Amplitude 기준)
- [ ] Supabase 스키마 설계 확정

### 산출물
- `prd/requirements.md`
- `prd/ia.md`
- `prd/prd-main.md`
- `prd/pages/*.md`

---

## Phase 3 — 목업 데이터 생성

**담당**: 데이터 에이전트
**목표**: 분석에 사용할 현실적인 목업 데이터셋 생성 및 Supabase 업로드

### 작업 목록
- [ ] Python 환경 설정 (`data/scripts/requirements.txt`)
- [ ] 유저 데이터 생성 스크립트 (1,000명)
- [ ] 상품 데이터 생성 (50개 SKU, 카테고리별)
- [ ] 주문/주문상품 데이터 생성 (3,000건, 12개월, 계절성 반영)
- [ ] 세션/이벤트 로그 생성 (10,000건)
- [ ] 재고 변동 이력 생성
- [ ] 리뷰 데이터 생성 (500건)
- [ ] Supabase 스키마 마이그레이션 실행
- [ ] CSV → Supabase 업로드 스크립트

### 산출물
- `data/csv/*.csv` (7개 파일)
- `data/scripts/generate_data.py`
- `data/scripts/load_to_supabase.py`

---

## Phase 4 — 웹 앱 개발

**담당**: 개발 에이전트
**목표**: Next.js 기반 LUNA 쇼핑몰 구현 및 Vercel 배포

### 작업 목록
- [ ] Next.js 프로젝트 초기화 (`web/`)
- [ ] Supabase 클라이언트 설정
- [ ] Tailwind CSS + shadcn/ui 설정
- [ ] 레이아웃 (헤더, 푸터, 네비게이션)
- [ ] 홈페이지 구현
- [ ] 제품 목록 페이지 (필터, 정렬, 페이지네이션)
- [ ] 제품 상세 페이지
- [ ] 장바구니 기능 (Zustand)
- [ ] 결제 플로우 (모킹)
- [ ] 회원가입/로그인 (Supabase Auth)
- [ ] 마이페이지 (주문 내역)
- [ ] Vercel 배포 설정

### 산출물
- `web/` — 완성된 Next.js 앱
- Vercel 배포 URL

---

## Phase 5 — 분석 도구 연동

**담당**: 개발 에이전트, 데이터 에이전트
**목표**: GTM, Amplitude, Mixpanel 이벤트 추적 구현

### 작업 목록
- [ ] GTM 컨테이너 생성 및 웹 연동
- [ ] GTM 기본 태그 설정 (GA4, Amplitude, Mixpanel)
- [ ] 커스텀 이벤트 구현 (add_to_cart, purchase 등)
- [ ] Amplitude 대시보드 설정 (퍼널, 리텐션)
- [ ] Mixpanel 대시보드 설정 (이벤트 분석, 코호트)
- [ ] 이벤트 검증 (GTM Preview, Amplitude Debug)

### 산출물
- `web/lib/analytics/` — 이벤트 유틸 코드
- GTM 컨테이너 설정 문서
- Amplitude/Mixpanel 대시보드 스크린샷

---

## Phase 6 — 데이터 분석

**담당**: 데이터 에이전트
**목표**: 퍼널·RFM·리텐션·재고 분석 수행 및 인사이트 도출

### 작업 목록
- [ ] 퍼널 분석 쿼리 작성 및 실행
- [ ] RFM 세그먼테이션 (SQL + Python)
- [ ] 코호트 리텐션 분석
- [ ] 재고 회전율 분석
- [ ] 매출 분석 (월별, 카테고리, 채널)
- [ ] Tableau 대시보드 구성 (4개 시트)
- [ ] 분석 인사이트 문서화

### 산출물
- `data/queries/*.sql` (5개 파일)
- `data/scripts/rfm_analysis.py`
- `data/scripts/cohort_analysis.py`
- Tableau 대시보드 (.twbx)
- `prd/reports/data-insights.md`

---

## Phase 7 — 마케팅 전략

**담당**: 마케팅 에이전트
**목표**: 데이터 기반 마케팅 전략 및 캠페인 기획

### 작업 목록
- [ ] 페르소나 고도화 (Phase 6 분석 결과 반영)
- [ ] 채널별 마케팅 전략 수립
- [ ] 캠페인 기획 (인스타그램, 카카오 친구톡)
- [ ] 카피라이팅 자산 작성 (슬로건, 제품 설명, CTA)
- [ ] 콘텐츠 캘린더 (1개월분)
- [ ] 마케팅 인사이트 리포트

### 산출물
- `prd/marketing/personas.md` (최종)
- `prd/marketing/campaign-plan.md`
- `prd/marketing/copy-bank.md`
- `prd/marketing/insight-report.md`

---

## Phase 8 — 최종 보고

**담당**: 보고 에이전트
**목표**: 포트폴리오 제출용 종합 리포트 완성

### 작업 목록
- [ ] 전체 프로젝트 요약 리포트
- [ ] 데이터 분석 핵심 인사이트 정리
- [ ] 비즈니스 임팩트 & 추천 액션
- [ ] Tableau 대시보드 가이드 문서
- [ ] 포트폴리오 README 작성 (GitHub)
- [ ] 최종 GitHub 푸시 및 Vercel URL 정리

### 산출물
- `prd/reports/portfolio-deck.md`
- `prd/reports/final-insights.md`
- `README.md` (GitHub 포트폴리오용)

---

## 진행 현황

| Phase | 상태 | 시작일 | 완료일 |
|-------|------|--------|--------|
| 0: 초기 셋업 | ✅ 완료 | 2026-03-20 | 2026-03-20 |
| 1: 브랜드 전략 | ⏳ 대기 | - | - |
| 2: 기능 기획 | ⏳ 대기 | - | - |
| 3: 목업 데이터 | ⏳ 대기 | - | - |
| 4: 웹 앱 개발 | ⏳ 대기 | - | - |
| 5: 분석 연동 | ⏳ 대기 | - | - |
| 6: 데이터 분석 | ⏳ 대기 | - | - |
| 7: 마케팅 전략 | ⏳ 대기 | - | - |
| 8: 최종 보고 | ⏳ 대기 | - | - |
