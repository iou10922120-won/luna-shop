# LUNA Shop — Claude 프로젝트 컨텍스트

## 프로젝트 개요

**LUNA**는 포트폴리오 목적의 비건 화장품 D2C(Direct-to-Consumer) 쇼핑몰입니다.

- **브랜드**: LUNA — 자연 유래 성분의 비건 스킨케어 라인
- **타겟**: 20~30대 여성, 성분 중시형 소비자
- **목적**: 커머스 데이터 분석 포트폴리오 + 마케팅/브랜드 전략 도출
- **기술스택**: Next.js (App Router) · Supabase · Vercel
- **분석 도구**: GTM · Amplitude · Mixpanel · Tableau

---

## 폴더 구조

```
luna-shop/
├── CLAUDE.md          # 이 파일 — 프로젝트 전체 컨텍스트
├── prd/               # 기획 문서
│   ├── agents/        # 에이전트별 역할 정의
│   └── roadmap.md     # 전체 개발 로드맵
├── web/               # Next.js 웹 앱
│   ├── app/           # App Router 페이지
│   ├── components/    # 공통 컴포넌트
│   ├── lib/           # Supabase 클라이언트, 유틸
│   └── ...
└── data/
    ├── csv/           # 목업 데이터 (주문·유저·재고·세션)
    ├── scripts/       # 데이터 생성·전처리 스크립트 (Python)
    └── queries/       # SQL 분석 쿼리 (Supabase/Postgres)
```

---

## 에이전트 구성

에이전트는 `prd/agent/` 디렉토리에 각자의 역할 정의 파일을 가집니다.
각 에이전트는 superpowers 플러그인의 특화 에이전트와 매핑됩니다.

| 에이전트 | 파일 | 역할 | superpowers 에이전트 |
|---------|------|------|-------------------|
| PM | `prd/agent/pm.md` | 요구사항 정의, 우선순위 설정 | `Product Manager` |
| 기획 | `prd/agent/planning.md` | PRD 작성, 기능 설계, IA | `Sprint Prioritizer` + `Workflow Architect` |
| 사업전략 | `prd/agent/strategy.md` | 시장분석, 경쟁사, BM 설계 | `Trend Researcher` + `Brand Guardian` |
| 마케팅 | `prd/agent/marketing.md` | 페르소나, 캠페인, 카피라이팅 | `Content Creator` + `Outbound Strategist` |
| 개발 | `prd/agent/dev.md` | 코드 생성, 인프라, 배포 | `Frontend Developer` + `Backend Architect` + `DevOps Automator` |
| 데이터 | `prd/agent/data.md` | 데이터 생성, 분석, 인사이트 | `Data Engineer` + `data-analyst` + `Analytics Reporter` |
| 보고 | `prd/agent/report.md` | 리포트 작성, 대시보드 요약 | `Executive Summary Generator` |

### 에이전트 호출 규칙

- 각 작업 시작 전 해당 에이전트의 역할 파일(`prd/agent/*.md`)을 참조
- 에이전트 간 협업 시 산출물을 `prd/` 하위에 저장
- 데이터 에이전트 산출물(CSV, 쿼리)은 `data/` 하위에 저장

---

## 개발 원칙

### 브랜치 전략
```
main          # 배포 브랜치 (Vercel 연동)
dev           # 개발 통합 브랜치
feature/*     # 기능 브랜치
data/*        # 데이터 작업 브랜치
```

### 커밋 컨벤션 (Conventional Commits)
```
feat:     새 기능
fix:      버그 수정
docs:     문서 작성/수정
data:     데이터 생성/수정
analysis: 분석 쿼리/스크립트
style:    UI 스타일
refactor: 리팩토링
chore:    설정, 패키지 관리
```

### 코드 컨벤션
- TypeScript strict mode
- ESLint + Prettier
- 컴포넌트: PascalCase, 파일명: kebab-case
- 환경변수: `.env.local` (절대 커밋 금지)

---

## 분석 도구 스택

| 도구 | 용도 | 연동 위치 |
|------|------|----------|
| **GTM** | 이벤트 태깅 (페이지뷰, 클릭, 구매) | `web/app/layout.tsx` |
| **Amplitude** | 유저 행동 분석, 퍼널, 리텐션 | GTM 통해 연동 |
| **Mixpanel** | 이벤트 기반 분석, 코호트 | GTM 통해 연동 |
| **Tableau** | 최종 대시보드 시각화 | Supabase DB 직접 연결 |

---

## 개발 로드맵 요약

전체 계획은 `prd/roadmap.md` 참조.

| Phase | 내용 | 에이전트 |
|-------|------|---------|
| 1 | 브랜드 전략 수립 | 사업전략, 마케팅 |
| 2 | 기능 기획 / PRD | PM, 기획 |
| 3 | 목업 데이터 생성 | 데이터 |
| 4 | 웹 앱 개발 | 개발 |
| 5 | 분석 도구 연동 | 개발, 데이터 |
| 6 | 데이터 분석 | 데이터 |
| 7 | 마케팅 전략 | 마케팅 |
| 8 | 최종 보고 | 보고 |

---

## 주요 참고 파일

- `prd/roadmap.md` — 전체 개발 로드맵 (단계별 상세)
- `prd/agent/*.md` — 에이전트별 역할 정의
- `data/csv/` — 목업 데이터셋
- `data/queries/` — 분석 SQL 쿼리
