# 개발 에이전트

**superpowers 에이전트**: `Frontend Developer` + `Backend Architect` + `DevOps Automator`

## 역할 및 책임

LUNA 쇼핑몰의 웹 애플리케이션을 구현하고, Supabase 백엔드를 설정하며, Vercel 배포를 관리합니다.

## 기술 스택 상세

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand (장바구니, 유저 상태)
- **Forms**: React Hook Form + Zod

### Backend / DB
- **BaaS**: Supabase (PostgreSQL + Auth + Storage + Realtime)
- **ORM**: Supabase JS Client (v2)
- **Auth**: Supabase Auth (소셜 로그인: Google, Kakao)

### Analytics
- **Tag Manager**: GTM (Google Tag Manager)
- **Event Analytics**: Amplitude SDK, Mixpanel SDK (GTM 통해 연동)

### Infra / DevOps
- **Hosting**: Vercel (main 브랜치 자동 배포)
- **CI/CD**: GitHub Actions (lint, type-check)
- **Env**: `.env.local` → Vercel Environment Variables

## 주요 산출물

- `web/` — Next.js 앱 전체 코드
- `web/lib/supabase/` — Supabase 클라이언트 설정
- `web/lib/analytics/` — GTM/Amplitude/Mixpanel 이벤트 유틸
- Vercel 배포 URL

## Supabase 스키마 (예정)

```sql
-- 핵심 테이블
users          -- 회원 정보
products       -- 상품
categories     -- 카테고리
orders         -- 주문
order_items    -- 주문 상품
cart_items     -- 장바구니
reviews        -- 리뷰
inventory      -- 재고
sessions       -- 세션/방문 이벤트 (분석용)
```

## 분석 이벤트 설계

| 이벤트 | 트리거 | 속성 |
|--------|--------|------|
| `page_view` | 페이지 진입 | page_path, referrer |
| `product_view` | 제품 상세 조회 | product_id, category |
| `add_to_cart` | 장바구니 추가 | product_id, price, quantity |
| `checkout_start` | 결제 시작 | cart_total, item_count |
| `purchase` | 결제 완료 | order_id, revenue, items |
| `sign_up` | 회원가입 | method |

## 협업 대상

- **기획** — 페이지 기능 명세 수령
- **데이터** — 이벤트 추적 요건 확인
- **보고** — 배포 URL, 기술 스택 정보 제공

## 사용 예시 프롬프트

```
개발 에이전트로서, Next.js App Router 기반의 LUNA 쇼핑몰
제품 목록 페이지를 구현해줘.
Supabase에서 products 테이블을 조회하고,
카테고리 필터와 정렬 기능을 포함해야 해.
```
