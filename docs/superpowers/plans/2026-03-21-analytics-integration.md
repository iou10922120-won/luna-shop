# Phase 5: Analytics Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GTM/Amplitude/Mixpanel 이벤트 추적 코드를 LUNA 쇼핑몰에 삽입하여, 환경변수만 넣으면 바로 데이터 수집이 시작되도록 한다.

**Architecture:** 단일 `track()` 함수가 GTM dataLayer, Amplitude, Mixpanel 3곳에 동시 발송. 환경변수 없으면 console.log fallback. 서버 컴포넌트는 analytics 호출 불가 — 클라이언트 래퍼 컴포넌트에서 처리.

**Tech Stack:** Next.js 16 App Router, TypeScript, @amplitude/analytics-browser, mixpanel-browser

---

## File Structure

```
web/src/lib/analytics/
├── types.ts          — 이벤트명 enum + 이벤트별 속성 타입 (PRD 16종)
├── gtm.ts            — GTM dataLayer push 래퍼
├── amplitude.ts      — Amplitude SDK init + track 래퍼
├── mixpanel.ts       — Mixpanel SDK init + track 래퍼
├── index.ts          — 통합 track() 함수 + init()
└── provider.tsx      — AnalyticsProvider 클라이언트 컴포넌트 (init 호출 + page_view 자동 추적)

web/src/app/layout.tsx           — (수정) GTM 스크립트 + AnalyticsProvider 래핑
web/src/app/products/[slug]/
  └── add-to-cart-button.tsx      — (수정) add_to_cart 이벤트
  └── page.tsx                    — (수정) product_view 이벤트용 클라이언트 래퍼 추가
web/src/app/products/page.tsx     — (수정) product_list_view, product_list_filter 이벤트용 클라이언트 래퍼 추가
web/src/app/cart/page.tsx         — (수정) cart_view, remove_from_cart 이벤트
web/src/app/checkout/page.tsx     — (수정) checkout_start, purchase 이벤트
web/src/app/mypage/page.tsx       — (수정) login 이벤트
prd/analytics-setup.md            — GTM/Amplitude/Mixpanel 설정 가이드 문서
```

---

### Task 1: Analytics 타입 정의

**Files:**
- Create: `web/src/lib/analytics/types.ts`

- [ ] **Step 1: 이벤트명 enum 작성**

PRD 섹션 5의 16종 이벤트를 타입으로 정의:

```typescript
export enum AnalyticsEvent {
  SESSION_START = 'session_start',
  PAGE_VIEW = 'page_view',
  PRODUCT_LIST_VIEW = 'product_list_view',
  PRODUCT_LIST_FILTER = 'product_list_filter',
  PRODUCT_VIEW = 'product_view',
  INGREDIENT_VIEW = 'ingredient_view',
  ADD_TO_CART = 'add_to_cart',
  REMOVE_FROM_CART = 'remove_from_cart',
  CART_VIEW = 'cart_view',
  CHECKOUT_START = 'checkout_start',
  PURCHASE = 'purchase',
  SIGNUP_START = 'signup_start',
  SIGNUP_COMPLETE = 'signup_complete',
  LOGIN = 'login',
  REVIEW_WRITE = 'review_write',
  COUPON_APPLY = 'coupon_apply',
}
```

- [ ] **Step 2: 이벤트별 속성 인터페이스 작성**

PRD의 이벤트별 속성을 TypeScript 인터페이스로 정의. `EventProperties` 맵 타입으로 track() 함수에 타입 안전성 부여:

```typescript
export interface PageViewProps {
  page_path: string;
  page_title: string;
}

export interface ProductViewProps {
  product_id: string;
  product_name: string;
  category: string;
  price: number;
  sale_price: number | null;
}

export interface AddToCartProps {
  product_id: string;
  product_name: string;
  category: string;
  price: number;
  quantity: number;
  cart_total: number;
  cart_item_count: number;
}

export interface RemoveFromCartProps {
  product_id: string;
  product_name: string;
}

export interface PurchaseProps {
  order_id: string;
  order_number: string;
  total_amount: number;
  discount_amount: number;
  shipping_fee: number;
  item_count: number;
  items: Array<{
    product_id: string;
    category: string;
    quantity: number;
    price: number;
  }>;
  coupon_code?: string;
  payment_method: string;
}

export interface ProductListFilterProps {
  filter_type: string;
  filter_value: string;
}

export interface CheckoutStartProps {
  cart_total: number;
  item_count: number;
}

export interface LoginProps {
  method: string;
}

// 속성이 없거나 간단한 이벤트는 Record<string, unknown>
export type EventPropertiesMap = {
  [AnalyticsEvent.SESSION_START]: Record<string, never>;
  [AnalyticsEvent.PAGE_VIEW]: PageViewProps;
  [AnalyticsEvent.PRODUCT_LIST_VIEW]: { category?: string };
  [AnalyticsEvent.PRODUCT_LIST_FILTER]: ProductListFilterProps;
  [AnalyticsEvent.PRODUCT_VIEW]: ProductViewProps;
  [AnalyticsEvent.INGREDIENT_VIEW]: { product_id: string; product_name: string };
  [AnalyticsEvent.ADD_TO_CART]: AddToCartProps;
  [AnalyticsEvent.REMOVE_FROM_CART]: RemoveFromCartProps;
  [AnalyticsEvent.CART_VIEW]: { cart_total: number; item_count: number };
  [AnalyticsEvent.CHECKOUT_START]: CheckoutStartProps;
  [AnalyticsEvent.PURCHASE]: PurchaseProps;
  [AnalyticsEvent.SIGNUP_START]: Record<string, never>;
  [AnalyticsEvent.SIGNUP_COMPLETE]: Record<string, never>;
  [AnalyticsEvent.LOGIN]: LoginProps;
  [AnalyticsEvent.REVIEW_WRITE]: { product_id: string; rating: number };
  [AnalyticsEvent.COUPON_APPLY]: { coupon_code: string; discount_amount: number };
};
```

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/analytics/types.ts
git commit -m "feat: analytics 이벤트 타입 정의 (PRD 16종)"
```

---

### Task 2: GTM 유틸리티

**Files:**
- Create: `web/src/lib/analytics/gtm.ts`

- [ ] **Step 1: GTM dataLayer push 함수 작성**

```typescript
// window.dataLayer 타입 선언
declare global {
  interface Window {
    dataLayer?: Record<string, unknown>[];
  }
}

export function pushToDataLayer(event: string, properties: Record<string, unknown> = {}) {
  if (typeof window === 'undefined') return;

  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event,
    ...properties,
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/lib/analytics/gtm.ts
git commit -m "feat: GTM dataLayer push 유틸리티"
```

---

### Task 3: Amplitude 유틸리티

**Files:**
- Create: `web/src/lib/analytics/amplitude.ts`

- [ ] **Step 1: npm 패키지 설치**

```bash
cd web && npm install @amplitude/analytics-browser
```

- [ ] **Step 2: Amplitude 래퍼 작성**

```typescript
import * as amplitude from '@amplitude/analytics-browser';

let initialized = false;

export function initAmplitude() {
  const apiKey = process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY;
  if (!apiKey || initialized) return;

  amplitude.init(apiKey, {
    defaultTracking: false,
  });
  initialized = true;
}

export function trackAmplitude(event: string, properties: Record<string, unknown> = {}) {
  if (!initialized) return;
  amplitude.track(event, properties);
}
```

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/analytics/amplitude.ts web/package.json web/package-lock.json
git commit -m "feat: Amplitude SDK 래퍼"
```

---

### Task 4: Mixpanel 유틸리티

**Files:**
- Create: `web/src/lib/analytics/mixpanel.ts`

- [ ] **Step 1: npm 패키지 설치**

```bash
cd web && npm install mixpanel-browser && npm install -D @types/mixpanel-browser
```

- [ ] **Step 2: Mixpanel 래퍼 작성**

```typescript
import mixpanel from 'mixpanel-browser';

let initialized = false;

export function initMixpanel() {
  const token = process.env.NEXT_PUBLIC_MIXPANEL_TOKEN;
  if (!token || initialized) return;

  mixpanel.init(token, {
    track_pageview: false,
    persistence: 'localStorage',
  });
  initialized = true;
}

export function trackMixpanel(event: string, properties: Record<string, unknown> = {}) {
  if (!initialized) return;
  mixpanel.track(event, properties);
}
```

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/analytics/mixpanel.ts web/package.json web/package-lock.json
git commit -m "feat: Mixpanel SDK 래퍼"
```

---

### Task 5: 통합 Analytics 모듈

**Files:**
- Create: `web/src/lib/analytics/index.ts`

- [ ] **Step 1: 통합 init + track 함수 작성**

`init()`은 Amplitude/Mixpanel 초기화. `track()`은 3곳 동시 발송 (GTM dataLayer + Amplitude + Mixpanel). 키 없으면 console.log fallback.

```typescript
import { pushToDataLayer } from './gtm';
import { initAmplitude, trackAmplitude } from './amplitude';
import { initMixpanel, trackMixpanel } from './mixpanel';
import type { AnalyticsEvent, EventPropertiesMap } from './types';

const isDev = process.env.NODE_ENV === 'development';

export function initAnalytics() {
  initAmplitude();
  initMixpanel();
}

export function track<E extends AnalyticsEvent>(
  event: E,
  properties: EventPropertiesMap[E]
) {
  const props = properties as Record<string, unknown>;

  // GTM — always push (GTM script 없으면 dataLayer에만 쌓임)
  pushToDataLayer(event, props);

  // Amplitude
  trackAmplitude(event, props);

  // Mixpanel
  trackMixpanel(event, props);

  // Dev fallback — 키 없어도 콘솔에서 확인 가능
  if (isDev) {
    console.log(`[Analytics] ${event}`, props);
  }
}

export { AnalyticsEvent } from './types';
export type { EventPropertiesMap } from './types';
```

- [ ] **Step 2: Commit**

```bash
git add web/src/lib/analytics/index.ts
git commit -m "feat: 통합 analytics track() 함수 — GTM + Amplitude + Mixpanel"
```

---

### Task 6: AnalyticsProvider + GTM 스크립트

**Files:**
- Create: `web/src/lib/analytics/provider.tsx`
- Modify: `web/src/app/layout.tsx`

- [ ] **Step 1: AnalyticsProvider 클라이언트 컴포넌트 작성**

초기화 + `page_view` 자동 추적 (pathname 변경 감지):

```typescript
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { initAnalytics, track, AnalyticsEvent } from '@/lib/analytics';

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Init on mount
  useEffect(() => {
    initAnalytics();
  }, []);

  // Track page views on route change
  useEffect(() => {
    track(AnalyticsEvent.PAGE_VIEW, {
      page_path: pathname,
      page_title: document.title,
    });
  }, [pathname]);

  return <>{children}</>;
}
```

- [ ] **Step 2: layout.tsx에 GTM 스크립트 + AnalyticsProvider 추가**

`layout.tsx`에서:
1. `<head>`에 GTM 스크립트 삽입 (`NEXT_PUBLIC_GTM_ID` 없으면 스킵)
2. `<body>` 안에 GTM noscript iframe 삽입
3. children을 `<AnalyticsProvider>`로 래핑

```typescript
// layout.tsx 상단에 추가
import Script from "next/script";
import { AnalyticsProvider } from "@/lib/analytics/provider";

// GTM ID
const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID;
```

body 내부를 다음과 같이 수정:
```tsx
<body className="min-h-full flex flex-col font-sans">
  {GTM_ID && (
    <noscript>
      <iframe
        src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`}
        height="0"
        width="0"
        style={{ display: 'none', visibility: 'hidden' }}
      />
    </noscript>
  )}
  <AnalyticsProvider>
    <Header />
    <main className="flex-1">{children}</main>
    <Footer />
  </AnalyticsProvider>
  {GTM_ID && (
    <Script
      id="gtm-script"
      strategy="afterInteractive"
      dangerouslySetInnerHTML={{
        __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
          new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
          j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
          'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
          })(window,document,'script','dataLayer','${GTM_ID}');`,
      }}
    />
  )}
</body>
```

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/analytics/provider.tsx web/src/app/layout.tsx
git commit -m "feat: AnalyticsProvider + GTM 스크립트 layout 삽입"
```

---

### Task 7: 제품 상세 페이지 이벤트 (product_view, ingredient_view)

**Files:**
- Create: `web/src/app/products/[slug]/product-tracker.tsx`
- Modify: `web/src/app/products/[slug]/page.tsx`

제품 상세 페이지는 서버 컴포넌트(async). 클라이언트 래퍼 컴포넌트를 만들어 마운트 시 `product_view` 발송.

- [ ] **Step 1: ProductTracker 클라이언트 컴포넌트 작성**

```typescript
'use client';

import { useEffect } from 'react';
import { track, AnalyticsEvent } from '@/lib/analytics';

interface Props {
  productId: string;
  productName: string;
  category: string;
  price: number;
  salePrice: number | null;
}

export function ProductTracker({ productId, productName, category, price, salePrice }: Props) {
  useEffect(() => {
    track(AnalyticsEvent.PRODUCT_VIEW, {
      product_id: productId,
      product_name: productName,
      category,
      price,
      sale_price: salePrice,
    });
  }, [productId, productName, category, price, salePrice]);

  return null;
}
```

- [ ] **Step 2: page.tsx에 ProductTracker 삽입**

`page.tsx` 상단 import에 추가:
```typescript
import { ProductTracker } from "./product-tracker";
```

return JSX 최상위 `<div>` 바로 안쪽 첫 줄에 삽입:
```tsx
<ProductTracker
  productId={product.id}
  productName={product.name}
  category={product.category?.name ?? ''}
  price={product.price}
  salePrice={product.sale_price}
/>
```

- [ ] **Step 3: 성분 정보 섹션에 ingredient_view 이벤트 추가**

성분 정보 영역은 항상 보이므로, 스크롤로 뷰포트 진입 시 추적하거나 단순히 product_view에 포함시킬 수 있음. 포트폴리오 목적이므로 **성분 섹션 영역이 렌더링될 때 ProductTracker에서 함께 발송**하는 간단한 방식 채택:

ProductTracker에 `hasIngredients` prop 추가, true일 때 `ingredient_view`도 발송:

```typescript
// ProductTracker props에 추가
hasIngredients?: boolean;

// useEffect 안에 추가
if (hasIngredients) {
  track(AnalyticsEvent.INGREDIENT_VIEW, {
    product_id: productId,
    product_name: productName,
  });
}
```

page.tsx에서 prop 전달:
```tsx
<ProductTracker
  ...
  hasIngredients={!!product.ingredient_details?.length}
/>
```

- [ ] **Step 4: Commit**

```bash
git add web/src/app/products/\[slug\]/product-tracker.tsx web/src/app/products/\[slug\]/page.tsx
git commit -m "feat: 제품 상세 product_view + ingredient_view 이벤트"
```

---

### Task 8: add_to_cart 이벤트

**Files:**
- Modify: `web/src/app/products/[slug]/add-to-cart-button.tsx`

- [ ] **Step 1: track import 추가 및 handleAdd에 이벤트 삽입**

```typescript
// 상단 import 추가
import { track, AnalyticsEvent } from '@/lib/analytics';
import { useCartStore } from '@/lib/store';
```

`handleAdd` 함수 내부, `addItem(product, quantity)` 뒤에:
```typescript
const handleAdd = () => {
  addItem(product, quantity);

  // Analytics
  const store = useCartStore.getState();
  track(AnalyticsEvent.ADD_TO_CART, {
    product_id: product.id,
    product_name: product.name,
    category: product.category?.name ?? '',
    price: product.sale_price ?? product.price,
    quantity,
    cart_total: store.totalPrice(),
    cart_item_count: store.totalItems(),
  });

  setAdded(true);
  setTimeout(() => setAdded(false), 2000);
};
```

- [ ] **Step 2: Commit**

```bash
git add web/src/app/products/\[slug\]/add-to-cart-button.tsx
git commit -m "feat: add_to_cart 이벤트 추적"
```

---

### Task 9: 제품 목록 페이지 이벤트 (product_list_view, product_list_filter)

**Files:**
- Create: `web/src/app/products/product-list-tracker.tsx`
- Modify: `web/src/app/products/page.tsx`

제품 목록도 서버 컴포넌트이므로 클라이언트 래퍼 필요.

- [ ] **Step 1: ProductListTracker 클라이언트 컴포넌트 작성**

```typescript
'use client';

import { useEffect, useRef } from 'react';
import { track, AnalyticsEvent } from '@/lib/analytics';

interface Props {
  category?: string;
}

export function ProductListTracker({ category }: Props) {
  const prevCategory = useRef(category);

  useEffect(() => {
    track(AnalyticsEvent.PRODUCT_LIST_VIEW, {
      category: category ?? undefined,
    });
  }, [category]);

  useEffect(() => {
    if (prevCategory.current !== category && category) {
      track(AnalyticsEvent.PRODUCT_LIST_FILTER, {
        filter_type: 'category',
        filter_value: category,
      });
    }
    prevCategory.current = category;
  }, [category]);

  return null;
}
```

- [ ] **Step 2: page.tsx에 ProductListTracker 삽입**

import 추가:
```typescript
import { ProductListTracker } from "./product-list-tracker";
```

return JSX 최상위 `<div>` 바로 안쪽 첫 줄에:
```tsx
<ProductListTracker category={categorySlug} />
```

- [ ] **Step 3: Commit**

```bash
git add web/src/app/products/product-list-tracker.tsx web/src/app/products/page.tsx
git commit -m "feat: 제품 목록 product_list_view + product_list_filter 이벤트"
```

---

### Task 10: 장바구니 페이지 이벤트 (cart_view, remove_from_cart)

**Files:**
- Modify: `web/src/app/cart/page.tsx`

장바구니는 이미 클라이언트 컴포넌트("use client")이므로 직접 track 호출.

- [ ] **Step 1: cart_view 이벤트 — 페이지 마운트 시**

import 추가:
```typescript
import { track, AnalyticsEvent } from '@/lib/analytics';
```

컴포넌트 상단 (items.length === 0 체크 전)에 useEffect 추가:
```typescript
useEffect(() => {
  if (items.length > 0) {
    track(AnalyticsEvent.CART_VIEW, {
      cart_total: totalPrice(),
      item_count: items.length,
    });
  }
}, []); // 마운트 시 1회
```

`useEffect` import도 추가:
```typescript
import { useState, useEffect } from 'react'; // 기존에 useState 없으면 추가
```

참고: cart/page.tsx는 현재 useState를 사용하지 않으나 useEffect를 import 해야 함. 기존 import에 추가.

- [ ] **Step 2: remove_from_cart 이벤트 — 삭제 버튼 클릭 시**

삭제 버튼 onClick을 래핑:
```tsx
onClick={() => {
  track(AnalyticsEvent.REMOVE_FROM_CART, {
    product_id: item.product.id,
    product_name: item.product.name,
  });
  removeItem(item.product.id);
}}
```

- [ ] **Step 3: Commit**

```bash
git add web/src/app/cart/page.tsx
git commit -m "feat: cart_view + remove_from_cart 이벤트"
```

---

### Task 11: 결제 페이지 이벤트 (checkout_start, purchase)

**Files:**
- Modify: `web/src/app/checkout/page.tsx`

결제 페이지도 이미 클라이언트 컴포넌트.

- [ ] **Step 1: checkout_start — 페이지 마운트 시**

import 추가:
```typescript
import { track, AnalyticsEvent } from '@/lib/analytics';
```

기존 useEffect가 없으므로 추가 (items 빈 배열 체크 전에는 불가, 체크 후에 넣어야 함):

items.length === 0 && !completed 체크가 router.push를 하기 때문에, 그 아래에서 useEffect로 checkout_start 발송:

```typescript
useEffect(() => {
  if (items.length > 0 && !completed) {
    track(AnalyticsEvent.CHECKOUT_START, {
      cart_total: totalPrice(),
      item_count: items.length,
    });
  }
}, []); // 마운트 시 1회
```

주의: 이 useEffect는 items.length === 0 체크 뒤에 올 수 없음 (early return 때문에 hooks 순서 깨짐). `handleOrder` 함수 정의 전, shipping/total 계산 후에 배치.

실제로 checkout/page.tsx를 보면:
- line 17: `if (items.length === 0 && !completed)` → early return
- hooks는 early return 전에 모두 선언해야 함

따라서 line 16 (completed useState 뒤)와 line 17 (early return) 사이에 useEffect를 삽입:

```typescript
const [completed, setCompleted] = useState(false);

useEffect(() => {
  if (items.length > 0) {
    track(AnalyticsEvent.CHECKOUT_START, {
      cart_total: totalPrice(),
      item_count: items.length,
    });
  }
}, []);

if (items.length === 0 && !completed) {
  ...
}
```

`useEffect` import 추가:
```typescript
import { useState, useEffect } from "react";
```

- [ ] **Step 2: purchase — handleOrder에서 주문 완료 시**

`handleOrder` 함수에서 clearCart() 전에 purchase 이벤트 발송:

```typescript
const handleOrder = (e: React.FormEvent) => {
  e.preventDefault();

  const orderNumber = `LUNA-${Date.now().toString().slice(-8)}`;

  track(AnalyticsEvent.PURCHASE, {
    order_id: orderNumber,
    order_number: orderNumber,
    total_amount: total,
    discount_amount: 0,
    shipping_fee: shipping,
    item_count: items.length,
    items: items.map((item) => ({
      product_id: item.product.id,
      category: item.product.category?.name ?? '',
      quantity: item.quantity,
      price: item.product.sale_price ?? item.product.price,
    })),
    payment_method: 'card',
  });

  clearCart();
  setCompleted(true);
};
```

주문 완료 화면에서 주문번호를 이 변수로 표시하려면 orderNumber를 state로 관리해야 하지만, 기존 코드가 `Date.now()`를 JSX에서 직접 호출하므로 일관성을 위해 purchase 이벤트용으로만 사용.

- [ ] **Step 3: Commit**

```bash
git add web/src/app/checkout/page.tsx
git commit -m "feat: checkout_start + purchase 이벤트"
```

---

### Task 12: 마이페이지 login 이벤트

**Files:**
- Modify: `web/src/app/mypage/page.tsx`

- [ ] **Step 1: login 이벤트 — 폼 제출 시**

import 추가:
```typescript
import { track, AnalyticsEvent } from '@/lib/analytics';
```

폼 onSubmit 핸들러에서:
```typescript
onSubmit={(e) => {
  e.preventDefault();
  setIsLoggedIn(true);
  track(AnalyticsEvent.LOGIN, { method: 'email' });
}}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/app/mypage/page.tsx
git commit -m "feat: login 이벤트 추적"
```

---

### Task 13: 빌드 검증

- [ ] **Step 1: TypeScript 빌드 체크**

```bash
cd web && npx tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 2: Next.js 빌드**

```bash
cd web && npm run build
```

Expected: 빌드 성공

- [ ] **Step 3: 빌드 에러 있으면 수정 후 Commit**

---

### Task 14: Analytics 설정 가이드 문서

**Files:**
- Create: `prd/analytics-setup.md`

- [ ] **Step 1: GTM/Amplitude/Mixpanel 연동 가이드 작성**

다음 내용 포함:
1. 필요한 환경변수 3개 (`NEXT_PUBLIC_GTM_ID`, `NEXT_PUBLIC_AMPLITUDE_API_KEY`, `NEXT_PUBLIC_MIXPANEL_TOKEN`)
2. 각 서비스 계정 생성 방법 (간단한 절차)
3. GTM 컨테이너에서 Amplitude/Mixpanel 태그 설정하는 방법
4. 이벤트 목록 및 검증 방법 (GTM Preview, Amplitude Debugger, 브라우저 콘솔)
5. `.env.local` 예시

- [ ] **Step 2: Commit**

```bash
git add prd/analytics-setup.md
git commit -m "docs: GTM/Amplitude/Mixpanel 연동 가이드"
```

---

### Task 15: roadmap.md 업데이트 + 최종 커밋

**Files:**
- Modify: `prd/roadmap.md`

- [ ] **Step 1: Phase 5 상태를 ✅ 완료로 변경**

```markdown
| 5: 분석 연동 | ✅ 완료 | 2026-03-21 | 2026-03-21 |
```

- [ ] **Step 2: Commit**

```bash
git add prd/roadmap.md
git commit -m "docs: Phase 5 완료 상태 업데이트"
```
