# LUNA 분석 도구 연동 가이드

> Phase 5 산출물 — GTM, Amplitude, Mixpanel 연동 방법

---

## 1. 환경변수 설정

`web/.env.local` 파일에 아래 3개 키를 추가합니다:

```env
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
NEXT_PUBLIC_AMPLITUDE_API_KEY=your-amplitude-api-key
NEXT_PUBLIC_MIXPANEL_TOKEN=your-mixpanel-project-token
```

> 키가 없으면 analytics 코드는 자동으로 비활성화됩니다 (개발에 영향 없음).
> 개발 모드(`npm run dev`)에서는 콘솔에 `[Analytics]` 로그가 출력됩니다.

---

## 2. 서비스별 계정 생성

### GTM (Google Tag Manager)

1. [tagmanager.google.com](https://tagmanager.google.com) 접속
2. 계정 생성 → 컨테이너 이름: "LUNA Shop" → 플랫폼: "웹"
3. 컨테이너 ID (GTM-XXXXXXX) 복사 → `NEXT_PUBLIC_GTM_ID`에 입력

### Amplitude

1. [amplitude.com](https://amplitude.com) 가입 (무료 플랜)
2. 프로젝트 생성: "LUNA Shop"
3. Settings → Projects → API Key 복사 → `NEXT_PUBLIC_AMPLITUDE_API_KEY`에 입력

### Mixpanel

1. [mixpanel.com](https://mixpanel.com) 가입 (무료 플랜)
2. 프로젝트 생성: "LUNA Shop"
3. Settings → Project Settings → Token 복사 → `NEXT_PUBLIC_MIXPANEL_TOKEN`에 입력

---

## 3. GTM 태그 설정

GTM 컨테이너에서 Amplitude/Mixpanel을 태그로 연동할 수 있습니다.
현재 코드에서는 GTM과 별도로 Amplitude/Mixpanel SDK를 직접 호출하므로,
GTM은 주로 **GA4 연동**이나 **추가 마케팅 픽셀** 용도로 사용합니다.

### GA4 태그 추가 (선택)

1. GTM → 태그 → 새로 만들기
2. 태그 유형: "Google Analytics: GA4 구성"
3. 측정 ID 입력 (G-XXXXXXXXXX)
4. 트리거: "All Pages"
5. 게시

---

## 4. 구현된 이벤트 목록

| 이벤트명 | 트리거 위치 | 카테고리 |
|---------|-----------|---------|
| `page_view` | 모든 페이지 (자동) | 세션 |
| `product_list_view` | /products 진입 | 탐색 |
| `product_list_filter` | 카테고리 필터 변경 | 탐색 |
| `product_view` | /products/[slug] 진입 | 탐색 |
| `ingredient_view` | 성분 정보 있는 제품 조회 | 탐색 |
| `add_to_cart` | 장바구니 담기 클릭 | 전환 |
| `remove_from_cart` | 장바구니 삭제 클릭 | 전환 |
| `cart_view` | /cart 진입 | 전환 |
| `checkout_start` | /checkout 진입 | 전환 |
| `purchase` | 결제 완료 | 전환 (매출) |
| `login` | 로그인 완료 | 인증 |

---

## 5. 이벤트 검증 방법

### 브라우저 콘솔 (개발 모드)

```bash
npm run dev
```

페이지 이동/버튼 클릭 시 콘솔에 `[Analytics] event_name {...}` 로그 확인.

### GTM Preview

1. GTM → 미리보기 → 사이트 URL 입력
2. Tag Assistant에서 이벤트 발생 확인

### Amplitude Debugger

1. Amplitude 대시보드 → User Look-Up
2. 실시간 이벤트 스트림 확인

### Mixpanel Live View

1. Mixpanel 대시보드 → Events → Live View
2. 실시간 이벤트 확인

---

## 6. 코드 구조

```
web/src/lib/analytics/
├── types.ts      — 이벤트명 enum + 속성 타입
├── gtm.ts        — GTM dataLayer push
├── amplitude.ts  — Amplitude SDK 래퍼
├── mixpanel.ts   — Mixpanel SDK 래퍼
├── index.ts      — 통합 track() 함수
└── provider.tsx  — AnalyticsProvider (page_view 자동 추적)
```

`track()` 함수 하나로 GTM + Amplitude + Mixpanel 3곳에 동시 발송됩니다.
