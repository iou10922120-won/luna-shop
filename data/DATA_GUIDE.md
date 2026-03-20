# LUNA Shop 데이터 삽입 가이드

## 개요

12개월치(2025-04 ~ 2026-03) 비건 화장품 D2C 커머스 목업 데이터를 생성하고,
Supabase / Amplitude / Mixpanel에 삽입하는 과정을 정리한 문서입니다.

## 데이터 규모

| 테이블 | 건수 | 설명 |
|--------|------|------|
| categories | 5 | 클렌저, 토너, 세럼, 크림, 선크림 |
| products | 50 | 카테고리별 10개, 실제 성분/가격 반영 |
| users | 1,000 | 한국 여성 중심, 가입채널/UTM 포함 |
| orders | 3,000 | 12개월 분산, 계절성 반영 |
| order_items | 5,145 | 주문당 1-3개 상품 |
| sessions | 16,105 | 5,000 세션, 퍼널 이벤트 16종 |
| inventory | 5,177 | 입고/판매/반품/조정 이력 |
| reviews | 500 | 자연스러운 한국어 리뷰 텍스트 |

**요약 테이블** (쿼리 성능 최적화용):
- daily_sales_summary — 일별 매출
- funnel_daily — 일별 퍼널 단계
- monthly_cohort — 월별 코호트 리텐션
- rfm_segments — 유저별 RFM 세그먼트
- product_performance — 상품별 성과

## 데이터에 심어진 패턴

분석 시 발견할 수 있도록 의도적으로 심은 패턴:

- **파레토 법칙**: 상위 10% VIP 유저가 전체 매출의 ~41.6% 차지
- **카테고리 전환율 차이**: 세럼/크림 > 클렌저 (고관여 제품이 전환율 높음)
- **채널 성과 차이**: Instagram > Naver 전환율
- **할인 효과**: 세일 상품이 ATC율 +10%p
- **계절성**: 봄/가을 피크, 여름/겨울 하락
- **요일 패턴**: 주말 > 평일 구매

---

## Step 1: 환경 설정

### 1-1. Python 패키지 설치

```bash
cd data/scripts
pip install -r requirements.txt
```

### 1-2. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성 (`.env.example` 참고):

```bash
cp .env.example .env
```

필요한 키:

| 변수 | 출처 | 용도 |
|------|------|------|
| `SUPABASE_URL` | Supabase > Settings > API | DB 접속 |
| `SUPABASE_KEY` | Supabase > Settings > API > service_role | DB 쓰기 권한 |
| `AMPLITUDE_API_KEY` | Amplitude > Settings > Projects | 이벤트 주입 |
| `MIXPANEL_PROJECT_TOKEN` | Mixpanel > Settings > Project | 이벤트 주입 |
| `MIXPANEL_PROJECT_ID` | Mixpanel > Settings > Project | Import API |
| `MIXPANEL_SERVICE_ACCOUNT_USERNAME` | Mixpanel > Settings > Service Accounts | Import API 인증 |
| `MIXPANEL_SERVICE_ACCOUNT_SECRET` | Mixpanel > Settings > Service Accounts | Import API 인증 |

---

## Step 2: CSV 데이터 생성

```bash
python generate_data.py
```

- `data/csv/` 폴더에 8개 CSV 파일 생성
- Seed=42로 고정 → 동일 데이터 재현 가능
- 이미 생성된 경우 이 단계는 건너뛰어도 됨

---

## Step 3: Supabase 테이블 생성

Supabase SQL Editor에서 `schema.sql` 실행:

1. Supabase Dashboard → SQL Editor
2. `data/scripts/schema.sql` 내용 전체 복사-붙여넣기
3. Run 클릭
4. 9개 원본 테이블 + 5개 요약 테이블 + 13개 인덱스 생성됨

---

## Step 4: CSV → Supabase 업로드

```bash
python load_to_supabase.py
```

### 동작 방식
- FK 의존 순서로 삽입: categories → products → users → orders → order_items → ...
- 500건씩 배치 INSERT (Supabase REST API)
- 배치 실패 시 개별 행 단위로 재시도
- 진행률 실시간 표시

### 옵션
```bash
python load_to_supabase.py --dry-run       # 실제 삽입 없이 검증만
python load_to_supabase.py --table users    # 특정 테이블만
python load_to_supabase.py --clean          # 기존 데이터 삭제 후 재삽입
```

### 주의사항
- `SUPABASE_KEY`는 반드시 **service_role_key** 사용 (anon key는 RLS에 의해 차단됨)
- 이미 데이터가 있으면 `--clean` 플래그로 초기화 후 재삽입

---

## Step 5: 요약 테이블 빌드

Supabase SQL Editor에서 `build_summaries.sql` 실행:

1. Supabase Dashboard → SQL Editor
2. `data/scripts/build_summaries.sql` 내용 전체 복사-붙여넣기
3. Run 클릭
4. 5개 요약 테이블에 데이터가 채워짐
5. 마지막 SELECT 쿼리로 각 테이블 건수 확인

### 기대 결과
| 테이블 | 예상 건수 |
|--------|-----------|
| daily_sales_summary | ~365 |
| funnel_daily | ~1,800 |
| monthly_cohort | ~80 |
| rfm_segments | ~800 |
| product_performance | 50 |

---

## Step 6: Amplitude / Mixpanel 이벤트 주입

```bash
python inject_analytics.py
```

### 동작 방식
- `sessions.csv`의 16,105개 이벤트를 API로 전송
- 2,000건씩 배치 전송
- 0.5초 간격으로 rate limiting 방지
- Amplitude HTTP API V2 + Mixpanel Import API 동시 지원

### 옵션
```bash
python inject_analytics.py --dry-run           # 전송 없이 샘플 확인
python inject_analytics.py --amplitude-only    # Amplitude만
python inject_analytics.py --mixpanel-only     # Mixpanel만
python inject_analytics.py --limit 100         # 100건만 테스트
```

### Amplitude 설정
- HTTP API V2 (`api2.amplitude.com/2/httpapi`)
- `user_id`: 로그인 유저 UUID
- `device_id`: 익명 유저 (`anon_세션ID`)
- 이벤트 속성: page_path, referrer, category, product 등

### Mixpanel 설정
- Import API (`api.mixpanel.com/import`)
- Service Account 인증 (Basic Auth)
- `distinct_id`: user_id 또는 `anon_세션ID`
- `$insert_id`: 이벤트 UUID (중복 방지)

### 비용
- Amplitude 무료 플랜: 월 50M 이벤트 → 16K건은 0.03%
- Mixpanel 무료 플랜: 월 20M 이벤트 → 16K건은 0.08%
- **비용 발생 없음**

---

## 전체 실행 순서 요약

```
1. pip install -r data/scripts/requirements.txt
2. .env 파일 생성 (환경변수 설정)
3. python data/scripts/generate_data.py          # CSV 생성 (이미 있으면 생략)
4. Supabase SQL Editor → schema.sql 실행         # 테이블 생성
5. python data/scripts/load_to_supabase.py       # CSV → Supabase
6. Supabase SQL Editor → build_summaries.sql 실행 # 요약 테이블 빌드
7. python data/scripts/inject_analytics.py       # 이벤트 → Amplitude/Mixpanel
```

---

## 트러블슈팅

### "permission denied" 오류
→ `SUPABASE_KEY`가 service_role_key인지 확인. anon key는 RLS 정책에 의해 차단됨.

### "duplicate key value violates unique constraint"
→ 이미 데이터가 있음. `--clean` 플래그로 초기화:
```bash
python load_to_supabase.py --clean
```

### Amplitude에 이벤트가 안 보임
→ Amplitude는 이벤트 처리에 최대 수분~수시간 소요. 1시간 후 재확인.

### Mixpanel Import 인증 실패
→ Service Account가 올바르게 생성되었는지 확인. Project Settings > Service Accounts에서 확인.
