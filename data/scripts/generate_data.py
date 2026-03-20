"""
LUNA Shop - 목업 데이터 생성 스크립트
=====================================
비건 화장품 D2C 쇼핑몰 포트폴리오용 12개월치 커머스 데이터 시뮬레이션

생성 테이블:
  1. categories   (5건)
  2. products     (50건)
  3. users        (1,000건)
  4. orders       (3,000건)
  5. order_items  (~5,000건)
  6. sessions     (5,000건)
  7. inventory    (~1,500건)
  8. reviews      (500건)

기간: 2025-04-01 ~ 2026-03-31 (12개월)
시간대: Asia/Seoul (UTC+9)
"""

import uuid
import random
import json
import math
import os
from datetime import datetime, timedelta, timezone, date
from collections import defaultdict

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# 0. 설정
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
fake = Faker("ko_KR")
Faker.seed(SEED)

KST = timezone(timedelta(hours=9))
START_DATE = datetime(2025, 4, 1, tzinfo=KST)
END_DATE = datetime(2026, 3, 31, 23, 59, 59, tzinfo=KST)
TOTAL_DAYS = (END_DATE.date() - START_DATE.date()).days + 1  # 366

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "csv")
os.makedirs(CSV_DIR, exist_ok=True)


def uuid4():
    return str(uuid.uuid4())


def kst_now():
    return datetime.now(KST)


def random_kst_datetime(start: datetime, end: datetime) -> datetime:
    """start~end 범위 안에서 무작위 KST datetime 반환."""
    delta = (end - start).total_seconds()
    offset = random.random() * delta
    return start + timedelta(seconds=offset)


# ---------------------------------------------------------------------------
# 1. Categories (5건)
# ---------------------------------------------------------------------------
print("=" * 60)
print("[1/8] categories 생성 중...")

CATEGORY_DEFS = [
    {"name": "클렌저", "slug": "cleanser", "display_order": 1},
    {"name": "토너",   "slug": "toner",    "display_order": 2},
    {"name": "세럼",   "slug": "serum",    "display_order": 3},
    {"name": "크림",   "slug": "cream",    "display_order": 4},
    {"name": "선크림", "slug": "sunscreen", "display_order": 5},
]

categories = []
for cd in CATEGORY_DEFS:
    categories.append({
        "id": uuid4(),
        "name": cd["name"],
        "slug": cd["slug"],
        "display_order": cd["display_order"],
        "created_at": START_DATE.isoformat(),
    })

cat_df = pd.DataFrame(categories)
cat_id_map = {c["slug"]: c["id"] for c in categories}
cat_name_map = {c["id"]: c["name"] for c in categories}

print(f"  -> {len(categories)}개 카테고리 생성 완료")

# ---------------------------------------------------------------------------
# 2. Products (50건 = 카테고리당 10개)
# ---------------------------------------------------------------------------
print("[2/8] products 생성 중...")

# 비건 화장품 성분 풀
VEGAN_INGREDIENTS = [
    "나이아신아마이드", "히알루론산", "세라마이드", "티트리", "캘린듈라",
    "알로에", "로즈마리", "녹차추출물", "병풀추출물(시카)", "판테놀",
    "스쿠알란", "호호바오일", "아르간오일", "비타민C", "비타민E",
    "코엔자임Q10", "프로폴리스", "마데카소사이드", "아데노신", "글리세린",
    "베타글루칸", "레시틴", "아줄렌", "카모마일추출물", "라벤더추출물",
    "백련추출물", "해바라기씨오일", "시어버터", "어성초추출물", "감초추출물",
]

INGREDIENT_ROLES = {
    "나이아신아마이드": "미백/톤 개선",
    "히알루론산": "보습",
    "세라마이드": "피부장벽 강화",
    "티트리": "진정/항균",
    "캘린듈라": "진정/보호",
    "알로에": "수분/진정",
    "로즈마리": "항산화",
    "녹차추출물": "항산화/진정",
    "병풀추출물(시카)": "재생/진정",
    "판테놀": "보습/진정",
    "스쿠알란": "보습/유연",
    "호호바오일": "보습/밸런싱",
    "아르간오일": "영양/탄력",
    "비타민C": "미백/항산화",
    "비타민E": "항산화/보호",
    "코엔자임Q10": "항산화/탄력",
    "프로폴리스": "영양/보호",
    "마데카소사이드": "진정/재생",
    "아데노신": "주름개선",
    "글리세린": "보습",
    "베타글루칸": "보습/면역강화",
    "레시틴": "유화/보습",
    "아줄렌": "진정/항염",
    "카모마일추출물": "진정",
    "라벤더추출물": "진정/항균",
    "백련추출물": "미백/보습",
    "해바라기씨오일": "보습/영양",
    "시어버터": "보습/보호",
    "어성초추출물": "진정/항균",
    "감초추출물": "진정/미백",
}

INGREDIENT_ORIGINS = ["한국", "프랑스", "일본", "호주", "독일", "미국", "스위스"]
INGREDIENT_GRADES = ["EWG 1등급", "EWG 2등급", "자체 인증"]

# 카테고리별 상품명 풀 (각 10개)
PRODUCT_NAMES = {
    "cleanser": [
        "캘린듈라 수딩 클렌징 젤",
        "그린티 딥 클렌징 폼",
        "히알루론 마일드 클렌저",
        "병풀 시카 클렌징 밀크",
        "티트리 포어 클린 워시",
        "알로에 수분 클렌징 폼",
        "카모마일 로우 pH 젤 클렌저",
        "로즈마리 리프레시 클렌저",
        "판테놀 소프트 클렌징 워터",
        "어성초 트러블 클렌징 젤",
    ],
    "toner": [
        "히알루론산 딥 하이드레이팅 토너",
        "녹차 밸런싱 토너",
        "병풀 시카 리페어 토너",
        "나이아신아마이드 브라이트닝 토너",
        "캘린듈라 카밍 토너",
        "판테놀 수분장벽 토너",
        "아줄렌 민감 진정 토너",
        "프로폴리스 영양 토너",
        "베타글루칸 보습 에센스 토너",
        "감초 화이트닝 토너",
    ],
    "serum": [
        "병풀 시카 리페어 세럼",
        "비타민C 브라이트닝 세럼",
        "히알루론산 3중 보습 앰플",
        "나이아신아마이드 포어 세럼",
        "세라마이드 장벽 리페어 앰플",
        "코엔자임Q10 탄력 세럼",
        "프로폴리스 글로우 앰플",
        "마데카 시카 앰플",
        "아데노신 링클 리페어 세럼",
        "스쿠알란 오일 세럼",
    ],
    "cream": [
        "세라마이드 장벽 크림",
        "시카 리페어 수분 크림",
        "히알루론산 워터 크림",
        "녹차 수분 진정 크림",
        "프로폴리스 너리싱 크림",
        "판테놀 시카 밤",
        "아르간 너리싱 나이트 크림",
        "비타민E 안티옥시던트 크림",
        "알로에 수딩 젤 크림",
        "베타글루칸 장벽 강화 크림",
    ],
    "sunscreen": [
        "데일리 UV 프로텍션 선크림 SPF50+",
        "시카 톤업 선크림 SPF50+",
        "그린티 선 에센스 SPF50+",
        "히알루론 수분 선젤 SPF50+",
        "캘린듈라 마일드 선로션 SPF45",
        "노세범 에어리 선스틱 SPF50+",
        "피지컬 미네랄 선크림 SPF42",
        "알로에 수딩 선크림 SPF50+",
        "톤업 글로우 선세럼 SPF50+",
        "민감피부 저자극 선밀크 SPF50+",
    ],
}

# 카테고리별 가격대
PRICE_RANGES = {
    "cleanser":  (18000, 28000),
    "toner":     (22000, 32000),
    "serum":     (32000, 48000),
    "cream":     (35000, 52000),
    "sunscreen": (24000, 35000),
}

# 카테고리별 상품 설명 템플릿
DESCRIPTION_TEMPLATES = {
    "cleanser": [
        "피부에 자극 없이 메이크업과 노폐물을 깨끗하게 제거하는 저자극 클렌저입니다. {ing} 성분이 세안 후에도 당김 없이 촉촉한 피부를 유지해줍니다.",
        "풍성한 거품으로 모공 속 노폐물까지 깨끗하게 세정하는 비건 클렌저입니다. {ing}(이)가 피부 진정에 도움을 줍니다.",
    ],
    "toner": [
        "세안 후 피부 pH 밸런스를 맞춰주는 약산성 토너입니다. {ing} 성분이 피부 결을 정돈하고 다음 스킨케어 흡수를 도와줍니다.",
        "풍부한 {ing} 성분으로 첫 단계부터 깊은 수분을 채워주는 에센스 토너입니다.",
    ],
    "serum": [
        "고농축 {ing} 성분이 피부 깊숙이 침투하여 집중 케어합니다. 가벼운 텍스처로 빠르게 흡수됩니다.",
        "{ing}(이)가 피부 고민을 타겟 케어하는 프리미엄 비건 세럼입니다.",
    ],
    "cream": [
        "진정과 보습을 동시에 잡는 {ing} 크림입니다. 민감한 피부도 편안하게 사용할 수 있는 저자극 처방입니다.",
        "{ing} 성분이 손상된 피부 장벽을 강화하고 하루 종일 촉촉함을 유지해줍니다.",
    ],
    "sunscreen": [
        "백탁 없이 가볍게 밀착되는 비건 선크림입니다. {ing} 성분이 자외선 차단과 동시에 피부를 보호합니다.",
        "높은 자외선 차단력과 {ing}(으)로 피부 케어까지 한 번에 해결하는 데일리 선케어입니다.",
    ],
}


def make_slug(cat_slug: str, product_name: str) -> str:
    """상품명을 URL-safe 슬러그로 변환."""
    # 간단하게 카테고리-인덱스 형태로 처리
    return f"{cat_slug}-{product_name.replace(' ', '-').lower()[:40]}"


def generate_ingredient_details(selected: list[str]) -> str:
    """성분 상세 정보 JSON 생성."""
    details = []
    for ing in selected:
        details.append({
            "name": ing,
            "role": INGREDIENT_ROLES.get(ing, "보습"),
            "origin": random.choice(INGREDIENT_ORIGINS),
            "grade": random.choices(INGREDIENT_GRADES, weights=[60, 30, 10])[0],
        })
    return json.dumps(details, ensure_ascii=False)


products = []
for cat_slug, names in PRODUCT_NAMES.items():
    cat_id = cat_id_map[cat_slug]
    price_lo, price_hi = PRICE_RANGES[cat_slug]
    descs = DESCRIPTION_TEMPLATES[cat_slug]

    for idx, pname in enumerate(names):
        price = random.randrange(price_lo, price_hi + 1, 1000)
        # 30% 확률로 할인가
        sale_price = None
        if random.random() < 0.30:
            discount_pct = random.uniform(0.10, 0.20)
            sale_price = int(price * (1 - discount_pct) / 100) * 100  # 100원 단위

        num_ingredients = random.randint(3, 8)
        selected_ingredients = random.sample(VEGAN_INGREDIENTS, num_ingredients)
        main_ing = selected_ingredients[0]

        desc = random.choice(descs).format(ing=main_ing)
        slug = f"{cat_slug}-{idx + 1:02d}"

        products.append({
            "id": uuid4(),
            "name": pname,
            "slug": slug,
            "description": desc,
            "price": price,
            "sale_price": sale_price,
            "category_id": cat_id,
            "image_url": f"/images/products/{slug}.webp",
            "ingredients": json.dumps(selected_ingredients, ensure_ascii=False),
            "ingredient_details": generate_ingredient_details(selected_ingredients),
            "is_vegan_certified": True,
            "stock_quantity": random.randint(50, 200),
            "created_at": START_DATE.isoformat(),
        })

prod_df = pd.DataFrame(products)
prod_id_list = [p["id"] for p in products]
prod_by_id = {p["id"]: p for p in products}
prod_cat_map = {p["id"]: p["category_id"] for p in products}

# 카테고리별 상품 ID 맵
cat_prod_ids = defaultdict(list)
for p in products:
    cat_slug_for_p = [s for s, cid in cat_id_map.items() if cid == p["category_id"]][0]
    cat_prod_ids[cat_slug_for_p].append(p["id"])

# 할인 상품 / 정가 상품 분리 (장바구니 추가율 차이용)
sale_product_ids = {p["id"] for p in products if p["sale_price"] is not None}
regular_product_ids = {p["id"] for p in products if p["sale_price"] is None}

print(f"  -> {len(products)}개 상품 생성 완료 (할인 상품 {len(sale_product_ids)}개)")

# ---------------------------------------------------------------------------
# 3. Users (1,000명)
# ---------------------------------------------------------------------------
print("[3/8] users 생성 중...")

# UTM 분포 정의
UTM_DIST = [
    # (source, medium, campaign, weight)
    ("google",    "organic",  None,              25),
    ("instagram", "social",   "brand_awareness", 20),
    ("naver",     "organic",  None,              15),
    ("kakao",     "cpc",      "spring_sale",     10),
    ("naver",     "blog",     "review_campaign",  10),
    ("youtube",   "social",   "influencer_collab", 5),
    (None,        None,       None,               15),  # direct
]
UTM_SOURCES  = [u[0] for u in UTM_DIST]
UTM_MEDIUMS  = [u[1] for u in UTM_DIST]
UTM_CAMPAIGNS = [u[2] for u in UTM_DIST]
UTM_WEIGHTS  = [u[3] for u in UTM_DIST]


def pick_utm() -> tuple:
    idx = random.choices(range(len(UTM_DIST)), weights=UTM_WEIGHTS)[0]
    return UTM_SOURCES[idx], UTM_MEDIUMS[idx], UTM_CAMPAIGNS[idx]


# 유저 생성일 분포: 성장 곡선 (지수적 증가)
def generate_user_signup_date() -> datetime:
    """12개월에 걸쳐 후반 편중 분포로 가입일 생성."""
    # beta(2, 5) -> 앞쪽 편중, beta(5, 2) -> 뒤쪽 편중
    t = random.betavariate(2.0, 1.2)  # 뒤쪽 편중
    days_offset = int(t * TOTAL_DAYS)
    dt = START_DATE + timedelta(days=days_offset)
    # 시간 랜덤
    dt = dt.replace(
        hour=random.randint(8, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
    )
    return dt


users = []
used_emails = set()

for i in range(1000):
    # 성별
    gender_roll = random.random()
    if gender_roll < 0.85:
        gender = "여성"
    elif gender_roll < 0.95:
        gender = "남성"
    else:
        gender = "선택안함"

    # 이름
    if gender == "남성":
        name = fake.name_male()
    else:
        name = fake.name_female()

    # 이메일 (중복 방지)
    base_email = fake.ascii_free_email()
    email = f"user{i+1:04d}_{base_email}"
    while email in used_emails:
        email = f"user{i+1:04d}_{random.randint(100,999)}_{base_email}"
    used_emails.add(email)

    # 생년월일 (1991~2004)
    birth_date = fake.date_of_birth(minimum_age=22, maximum_age=35)
    if birth_date.year < 1991:
        birth_date = birth_date.replace(year=random.randint(1991, 2004))
    elif birth_date.year > 2004:
        birth_date = birth_date.replace(year=random.randint(1991, 2004))

    # 가입 채널
    signup_channel = random.choices(["google", "kakao"], weights=[45, 55])[0]

    # UTM
    utm_source, utm_medium, utm_campaign = pick_utm()

    # 가입일
    created_at = generate_user_signup_date()

    phone = fake.phone_number()

    users.append({
        "id": uuid4(),
        "email": email,
        "name": name,
        "phone": phone,
        "gender": gender,
        "birth_date": birth_date.isoformat(),
        "signup_channel": signup_channel,
        "utm_source": utm_source,
        "utm_medium": utm_medium,
        "utm_campaign": utm_campaign,
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    })

user_df = pd.DataFrame(users)
user_ids = [u["id"] for u in users]
user_by_id = {u["id"]: u for u in users}

# UTM별 유저 분류 (전환율 차이 시뮬레이션용)
user_utm_map = {}
for u in users:
    user_utm_map[u["id"]] = u["utm_source"]

print(f"  -> {len(users)}명 유저 생성 완료")

# ---------------------------------------------------------------------------
# 4. Orders (3,000건) & Order Items (~5,000건)
# ---------------------------------------------------------------------------
print("[4/8] orders + order_items 생성 중...")

# VIP 유저 선정: 상위 10%가 매출 40% 차지
# -> 상위 100명은 주문 횟수 많고 고가 상품 비중 높음
# 파레토 분포로 유저별 주문 수 결정
NUM_ORDERS = 3000

# 주문 가능 유저 = 가입한 유저 (1000명 중 일부가 주문)
# 3000건 / 평균 3회 = ~1000명 유저 활용 (거의 전원 구매)
# 파레토 분포: shape=1.5 -> 소수 유저가 다수 주문

order_counts = []
for _ in range(1000):
    # 파레토 분포 + 최소 1회
    count = int(random.paretovariate(1.5))
    count = max(1, min(count, 15))
    order_counts.append(count)

# 총 주문 수 맞추기 위해 스케일링
total_raw = sum(order_counts)
scale = NUM_ORDERS / total_raw
order_counts = [max(1, round(c * scale)) for c in order_counts]

# 미세 조정
diff = NUM_ORDERS - sum(order_counts)
if diff > 0:
    for _ in range(diff):
        idx = random.randint(0, 999)
        order_counts[idx] += 1
elif diff < 0:
    for _ in range(-diff):
        candidates = [i for i in range(1000) if order_counts[i] > 1]
        if candidates:
            idx = random.choice(candidates)
            order_counts[idx] -= 1

# VIP 유저 (상위 10%): 주문 횟수 부스트
vip_indices = sorted(range(1000), key=lambda i: order_counts[i], reverse=True)[:100]
vip_user_ids = {user_ids[i] for i in vip_indices}

# 계절성 가중치 (월별)
# 3~4월: 봄 환절기 UP, 8월: 살짝 DOWN, 9~10월: 가을 환절기 UP, 1월: 신년세일 피크
MONTH_WEIGHTS = {
    4: 1.2,   # 2025-04 (봄 환절기)
    5: 1.0,
    6: 0.9,
    7: 0.85,
    8: 0.8,   # 여름 소폭 감소
    9: 1.15,  # 가을 환절기
    10: 1.2,  # 가을 환절기
    11: 1.0,
    12: 1.1,  # 연말
    1: 1.3,   # 신년세일 피크
    2: 0.95,
    3: 1.15,  # 봄 환절기 시작
}

# 요일 가중치 (0=월 ~ 6=일)
DOW_WEIGHTS = {0: 0.8, 1: 0.85, 2: 0.9, 3: 0.9, 4: 1.0, 5: 1.3, 6: 1.25}

# 카테고리별 상품 선택 가중치 (세럼/크림 인기)
CATEGORY_ORDER_WEIGHTS = {
    "cleanser": 15,
    "toner": 18,
    "serum": 28,    # 인기
    "cream": 25,    # 인기
    "sunscreen": 14,
}


def pick_order_datetime(user_created: datetime) -> datetime:
    """유저 가입일 이후, 계절성/요일 반영하여 주문일 생성."""
    # 가입일 ~ END_DATE 사이에서 가중치 적용 랜덤
    max_attempts = 100
    for _ in range(max_attempts):
        dt = random_kst_datetime(user_created, END_DATE)
        month_w = MONTH_WEIGHTS.get(dt.month, 1.0)
        dow_w = DOW_WEIGHTS.get(dt.weekday(), 1.0)
        combined = month_w * dow_w
        if random.random() < combined / 1.7:  # 1.7 = max possible weight
            # 시간대 분포: 점심(11-14), 저녁(19-23) 피크
            hour = random.choices(
                range(24),
                weights=[
                    1, 1, 0.5, 0.5, 0.3, 0.3, 0.5, 1,  # 0~7
                    2, 3, 4, 5, 5, 5, 4, 3,              # 8~15
                    3, 4, 5, 6, 7, 7, 5, 3,              # 16~23
                ]
            )[0]
            dt = dt.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
            return dt
    return random_kst_datetime(user_created, END_DATE)


def pick_products_for_order(is_vip: bool) -> list[dict]:
    """주문 상품 선택. VIP는 고가 상품(세럼/크림) 비중 높음."""
    # 주문당 상품 수: 1~4개 (평균 ~1.7)
    num_items = random.choices([1, 2, 3, 4], weights=[55, 25, 13, 7])[0]

    items = []
    chosen_product_ids = set()

    for _ in range(num_items):
        # 카테고리 선택
        if is_vip:
            weights = {k: v * (1.5 if k in ("serum", "cream") else 1.0)
                       for k, v in CATEGORY_ORDER_WEIGHTS.items()}
        else:
            weights = CATEGORY_ORDER_WEIGHTS

        cat_slug = random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
        )[0]

        available = [pid for pid in cat_prod_ids[cat_slug] if pid not in chosen_product_ids]
        if not available:
            available = cat_prod_ids[cat_slug]
        product_id = random.choice(available)
        chosen_product_ids.add(product_id)

        product = prod_by_id[product_id]
        unit_price = product["sale_price"] if product["sale_price"] else product["price"]
        quantity = random.choices([1, 2, 3], weights=[75, 20, 5])[0]

        items.append({
            "product_id": product_id,
            "unit_price": unit_price,
            "quantity": quantity,
            "subtotal": unit_price * quantity,
        })

    return items


# 쿠폰 정의
COUPONS = {
    "WELCOME10": {"type": "percent", "value": 10},   # 10% 할인
    "LUNA5000":  {"type": "fixed",   "value": 5000},  # 5000원 할인
}

orders = []
order_items = []
order_counter = defaultdict(int)  # 날짜별 주문번호 시퀀스

for user_idx in range(1000):
    user = users[user_idx]
    user_id = user["id"]
    user_created = datetime.fromisoformat(user["created_at"])
    n_orders = order_counts[user_idx]
    is_vip = user_id in vip_user_ids

    for _ in range(n_orders):
        ordered_at = pick_order_datetime(user_created)
        date_str = ordered_at.strftime("%Y%m%d")
        order_counter[date_str] += 1
        order_number = f"LUNA-{date_str}-{order_counter[date_str]:04d}"

        # 상품 선택
        items = pick_products_for_order(is_vip)
        subtotal = sum(it["subtotal"] for it in items)

        # 쿠폰 (20% 확률)
        coupon_code = None
        discount_amount = 0
        if random.random() < 0.20:
            coupon_code = random.choice(["WELCOME10", "LUNA5000"])
            cp = COUPONS[coupon_code]
            if cp["type"] == "percent":
                discount_amount = int(subtotal * cp["value"] / 100)
            else:
                discount_amount = cp["value"]
            discount_amount = min(discount_amount, subtotal)

        total_amount = subtotal - discount_amount

        # 배송비
        shipping_fee = 0 if total_amount >= 50000 else 3000
        total_amount += shipping_fee

        # 상태
        status = random.choices(
            ["paid", "delivered", "cancelled"],
            weights=[70, 25, 5],
        )[0]

        # 주문 시점 UTM (라스트 터치: 70% 확률로 유저 UTM, 30% 다른 채널)
        if random.random() < 0.70:
            o_utm_source = user["utm_source"]
            o_utm_medium = user["utm_medium"]
            o_utm_campaign = user["utm_campaign"]
        else:
            o_utm_source, o_utm_medium, o_utm_campaign = pick_utm()

        # 배송지
        shipping_address = json.dumps({
            "city": random.choice([
                "서울특별시", "경기도", "인천광역시", "부산광역시", "대구광역시",
                "대전광역시", "광주광역시", "울산광역시", "세종특별자치시",
                "강원특별자치도", "충청북도", "충청남도", "전라북도",
                "전라남도", "경상북도", "경상남도", "제주특별자치도",
            ]),
            "zipcode": fake.postcode(),
        }, ensure_ascii=False)

        order_id = uuid4()

        orders.append({
            "id": order_id,
            "user_id": user_id,
            "order_number": order_number,
            "status": status,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "shipping_fee": shipping_fee,
            "shipping_address": shipping_address,
            "coupon_code": coupon_code,
            "utm_source": o_utm_source,
            "utm_medium": o_utm_medium,
            "utm_campaign": o_utm_campaign,
            "ordered_at": ordered_at.isoformat(),
            "created_at": ordered_at.isoformat(),
        })

        for it in items:
            order_items.append({
                "id": uuid4(),
                "order_id": order_id,
                "product_id": it["product_id"],
                "quantity": it["quantity"],
                "unit_price": it["unit_price"],
                "subtotal": it["subtotal"],
            })

order_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)

# VIP 매출 비중 검증
vip_revenue = sum(o["total_amount"] for o in orders if o["user_id"] in vip_user_ids and o["status"] != "cancelled")
total_revenue = sum(o["total_amount"] for o in orders if o["status"] != "cancelled")
vip_pct = vip_revenue / total_revenue * 100 if total_revenue > 0 else 0

print(f"  -> {len(orders)}건 주문, {len(order_items)}건 주문상품 생성 완료")
print(f"     VIP(상위 10%) 매출 비중: {vip_pct:.1f}%")

# ---------------------------------------------------------------------------
# 5. Sessions (5,000건) - 퍼널 이벤트 시퀀스
# ---------------------------------------------------------------------------
print("[5/8] sessions (이벤트) 생성 중...")

# 퍼널 전환율 정의
# Visit -> ProductView: 45%
# ProductView -> AddToCart: 20%
# AddToCart -> Checkout: 55%
# Checkout -> Purchase: 80%

# 세럼/크림 전환율 보너스
CATEGORY_CONVERSION_BONUS = {
    "cleanser": 0.0,
    "toner": 0.0,
    "serum": 0.08,     # +8%p 전환율
    "cream": 0.06,     # +6%p 전환율
    "sunscreen": 0.0,
}

# instagram 유입 전환율 보너스
UTM_CONVERSION_BONUS = {
    "instagram": 0.05,
    "google": 0.0,
    "naver": -0.02,
    "kakao": 0.02,
    "youtube": 0.03,
    None: 0.0,
}

# 할인 상품 장바구니 추가 보너스
SALE_ATC_BONUS = 0.10  # +10%p

DEVICE_WEIGHTS = [65, 30, 5]  # mobile, desktop, tablet
DEVICE_TYPES = ["mobile", "desktop", "tablet"]

PAGE_PATHS = {
    "session_start": "/",
    "page_view": ["/", "/products", "/brand"],
    "product_list_view": "/products",
    "product_view": "/products/{slug}",
    "add_to_cart": "/products/{slug}",
    "checkout_start": "/checkout",
    "purchase": "/order/complete",
}

sessions_events = []
session_count = 0
NUM_SESSIONS = 5000

# 세션 시작일 분포 (유저 가입일 이후, 계절성 반영)
for _ in range(NUM_SESSIONS):
    session_count += 1
    session_id = f"sess_{uuid4()[:12]}_{session_count}"

    # 40% 로그인 세션, 60% 비로그인
    is_logged_in = random.random() < 0.40
    if is_logged_in:
        user = random.choice(users)
        user_id = user["id"]
        s_utm_source = user["utm_source"]
        s_utm_medium = user["utm_medium"]
        s_utm_campaign = user["utm_campaign"]
        user_created = datetime.fromisoformat(user["created_at"])
        session_start = random_kst_datetime(
            max(user_created, START_DATE),
            END_DATE,
        )
    else:
        user_id = None
        s_utm_source, s_utm_medium, s_utm_campaign = pick_utm()
        session_start = random_kst_datetime(START_DATE, END_DATE)

    device_type = random.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS)[0]

    # referrer 결정
    referrer = None
    if s_utm_source == "google":
        referrer = "https://www.google.com"
    elif s_utm_source == "instagram":
        referrer = "https://www.instagram.com"
    elif s_utm_source == "naver":
        referrer = "https://www.naver.com" if s_utm_medium == "organic" else "https://blog.naver.com"
    elif s_utm_source == "kakao":
        referrer = "https://www.kakao.com"
    elif s_utm_source == "youtube":
        referrer = "https://www.youtube.com"

    event_time = session_start
    base_event = {
        "session_id": session_id,
        "user_id": user_id,
        "utm_source": s_utm_source,
        "utm_medium": s_utm_medium,
        "utm_campaign": s_utm_campaign,
        "device_type": device_type,
        "referrer": referrer,
    }

    # --- 이벤트 시퀀스 생성 ---

    # 1) session_start
    sessions_events.append({
        **base_event,
        "id": uuid4(),
        "event_name": "session_start",
        "event_params": json.dumps({"entry_page": "/"}, ensure_ascii=False),
        "page_path": "/",
        "created_at": event_time.isoformat(),
    })
    event_time += timedelta(seconds=random.randint(1, 3))

    # 2) page_view (홈)
    sessions_events.append({
        **base_event,
        "id": uuid4(),
        "event_name": "page_view",
        "event_params": json.dumps({"page_title": "LUNA - 비건 스킨케어"}, ensure_ascii=False),
        "page_path": "/",
        "created_at": event_time.isoformat(),
    })
    event_time += timedelta(seconds=random.randint(5, 30))

    # 전환율 보너스 계산
    utm_bonus = UTM_CONVERSION_BONUS.get(s_utm_source, 0.0)

    # 3) product_list_view (50% 확률)
    if random.random() < 0.50:
        sessions_events.append({
            **base_event,
            "id": uuid4(),
            "event_name": "product_list_view",
            "event_params": json.dumps({"category": random.choice(["all", "cleanser", "toner", "serum", "cream", "sunscreen"])}, ensure_ascii=False),
            "page_path": "/products",
            "created_at": event_time.isoformat(),
        })
        event_time += timedelta(seconds=random.randint(10, 60))

    # 4) product_view (Visit->ProductView: 45%)
    pv_rate = 0.45 + utm_bonus
    if random.random() < pv_rate:
        # 상품 선택 (세럼/크림 가중치)
        viewed_product = random.choices(
            prod_id_list,
            weights=[
                CATEGORY_ORDER_WEIGHTS.get(
                    [s for s, cid in cat_id_map.items() if cid == prod_cat_map[pid]][0], 15
                )
                for pid in prod_id_list
            ],
        )[0]
        viewed_slug = prod_by_id[viewed_product]["slug"]
        viewed_cat_slug = [s for s, cid in cat_id_map.items() if cid == prod_cat_map[viewed_product]][0]
        cat_bonus = CATEGORY_CONVERSION_BONUS.get(viewed_cat_slug, 0.0)
        is_sale = viewed_product in sale_product_ids

        sessions_events.append({
            **base_event,
            "id": uuid4(),
            "event_name": "product_view",
            "event_params": json.dumps({
                "product_id": viewed_product,
                "product_name": prod_by_id[viewed_product]["name"],
                "category": cat_name_map.get(prod_cat_map[viewed_product], ""),
                "price": prod_by_id[viewed_product]["price"],
                "sale_price": prod_by_id[viewed_product]["sale_price"],
            }, ensure_ascii=False),
            "page_path": f"/products/{viewed_slug}",
            "created_at": event_time.isoformat(),
        })
        event_time += timedelta(seconds=random.randint(15, 120))

        # 5) add_to_cart (ProductView->AddToCart: 20%)
        atc_rate = 0.20 + cat_bonus + utm_bonus
        if is_sale:
            atc_rate += SALE_ATC_BONUS
        if random.random() < atc_rate:
            sessions_events.append({
                **base_event,
                "id": uuid4(),
                "event_name": "add_to_cart",
                "event_params": json.dumps({
                    "product_id": viewed_product,
                    "product_name": prod_by_id[viewed_product]["name"],
                    "quantity": 1,
                    "price": prod_by_id[viewed_product]["sale_price"] or prod_by_id[viewed_product]["price"],
                }, ensure_ascii=False),
                "page_path": f"/products/{viewed_slug}",
                "created_at": event_time.isoformat(),
            })
            event_time += timedelta(seconds=random.randint(10, 90))

            # 6) checkout_start (AddToCart->Checkout: 55%)
            co_rate = 0.55 + utm_bonus
            if random.random() < co_rate:
                sessions_events.append({
                    **base_event,
                    "id": uuid4(),
                    "event_name": "checkout_start",
                    "event_params": json.dumps({
                        "cart_value": prod_by_id[viewed_product]["sale_price"] or prod_by_id[viewed_product]["price"],
                    }, ensure_ascii=False),
                    "page_path": "/checkout",
                    "created_at": event_time.isoformat(),
                })
                event_time += timedelta(seconds=random.randint(30, 180))

                # 7) purchase (Checkout->Purchase: 80%)
                pur_rate = 0.80
                if random.random() < pur_rate:
                    sessions_events.append({
                        **base_event,
                        "id": uuid4(),
                        "event_name": "purchase",
                        "event_params": json.dumps({
                            "product_id": viewed_product,
                            "revenue": prod_by_id[viewed_product]["sale_price"] or prod_by_id[viewed_product]["price"],
                        }, ensure_ascii=False),
                        "page_path": "/order/complete",
                        "created_at": event_time.isoformat(),
                    })

sessions_df = pd.DataFrame(sessions_events)

# 퍼널 통계 계산
funnel_counts = sessions_df["event_name"].value_counts()
print(f"  -> {NUM_SESSIONS}개 세션, {len(sessions_events)}건 이벤트 생성 완료")
print(f"     이벤트 분포:")
for ev_name in ["session_start", "page_view", "product_list_view", "product_view", "add_to_cart", "checkout_start", "purchase"]:
    cnt = funnel_counts.get(ev_name, 0)
    print(f"       {ev_name}: {cnt}건")

# ---------------------------------------------------------------------------
# 6. Inventory (~1,500건)
# ---------------------------------------------------------------------------
print("[6/8] inventory 생성 중...")

inventory_records = []

# 각 상품별 재고 이력 생성
for product in products:
    pid = product["id"]
    initial_stock = product["stock_quantity"]

    # 초기 입고
    inventory_records.append({
        "id": uuid4(),
        "product_id": pid,
        "change_type": "inbound",
        "quantity_change": initial_stock,
        "quantity_after": initial_stock,
        "reason": "초기 입고",
        "created_at": START_DATE.isoformat(),
    })

    current_stock = initial_stock

    # 해당 상품의 판매 기록 추출
    product_order_items = [oi for oi in order_items if oi["product_id"] == pid]
    # 주문 ID -> 주문일 매핑
    order_date_map = {o["id"]: o["ordered_at"] for o in orders}

    # 판매 차감 기록
    for oi in product_order_items:
        order_date = order_date_map.get(oi["order_id"])
        if not order_date:
            continue
        # 주문 상태가 cancelled인 경우 스킵
        order_obj = next((o for o in orders if o["id"] == oi["order_id"]), None)
        if order_obj and order_obj["status"] == "cancelled":
            continue

        qty = oi["quantity"]
        current_stock -= qty
        if current_stock < 0:
            # 재입고 트리거
            restock_qty = random.randint(80, 150)
            current_stock += restock_qty
            inventory_records.append({
                "id": uuid4(),
                "product_id": pid,
                "change_type": "inbound",
                "quantity_change": restock_qty,
                "quantity_after": current_stock + qty,  # 판매 차감 전
                "reason": "재입고",
                "created_at": order_date,
            })

        inventory_records.append({
            "id": uuid4(),
            "product_id": pid,
            "change_type": "sale",
            "quantity_change": -qty,
            "quantity_after": current_stock,
            "reason": f"주문 판매",
            "created_at": order_date,
        })

    # 간헐적 반품 (판매 건의 3%)
    num_returns = max(1, int(len(product_order_items) * 0.03))
    for _ in range(num_returns):
        return_qty = 1
        current_stock += return_qty
        return_date = random_kst_datetime(START_DATE + timedelta(days=30), END_DATE)
        inventory_records.append({
            "id": uuid4(),
            "product_id": pid,
            "change_type": "return",
            "quantity_change": return_qty,
            "quantity_after": current_stock,
            "reason": "고객 반품",
            "created_at": return_date.isoformat(),
        })

    # 중간 재입고 1~2회 추가
    for _ in range(random.randint(1, 2)):
        restock_qty = random.randint(50, 120)
        current_stock += restock_qty
        restock_date = random_kst_datetime(
            START_DATE + timedelta(days=60),
            END_DATE - timedelta(days=30),
        )
        inventory_records.append({
            "id": uuid4(),
            "product_id": pid,
            "change_type": "inbound",
            "quantity_change": restock_qty,
            "quantity_after": current_stock,
            "reason": "정기 재입고",
            "created_at": restock_date.isoformat(),
        })

inventory_df = pd.DataFrame(inventory_records)
print(f"  -> {len(inventory_records)}건 재고 변동 기록 생성 완료")

# ---------------------------------------------------------------------------
# 7. Reviews (500건)
# ---------------------------------------------------------------------------
print("[7/8] reviews 생성 중...")

# 리뷰 평점 분포: 5점 40%, 4점 30%, 3점 15%, 2점 10%, 1점 5%
RATING_WEIGHTS = [5, 10, 15, 30, 40]  # 1~5점

# 리뷰 문장 풀
REVIEW_POOL = {
    5: [
        "진짜 인생템 찾았어요! 피부가 완전 달라졌습니다.",
        "비건 화장품이라 성분 걱정 없이 쓸 수 있어서 너무 좋아요.",
        "향도 은은하고 발림성도 최고예요. 재구매 확정!",
        "민감성인데 하나도 안 따갑고 진정 효과 확실해요.",
        "선물용으로 샀는데 너무 만족해서 제 것도 바로 주문했어요.",
        "사용감이 정말 가볍고 흡수가 빨라요. 강추합니다!",
        "피부 톤이 밝아진 게 눈에 보여요. 대만족!",
        "촉촉함이 하루 종일 유지돼요. 이 가격에 이 품질이라니!",
        "예민한 피부에도 자극 없이 순해요. 비건 인증이라 더 믿음이 가요.",
        "패키지도 예쁘고 제품력도 좋고, 루나 팬이 됐어요.",
        "트러블 피부인데 진짜 진정됐어요. 기적의 제품!",
        "세안 후 당김 없이 촉촉하고 피부결이 매끈해졌어요.",
        "쓰면 쓸수록 피부가 좋아지는 느낌이에요. 꾸준히 쓸게요.",
        "성분이 깨끗해서 안심하고 쓸 수 있어요. 가족 모두 애용 중!",
        "이 가격에 이 성분 구성이면 가성비 최고입니다.",
    ],
    4: [
        "전반적으로 만족합니다. 보습력이 좋아요.",
        "향이 살짝 강한 편이지만 효과는 확실해요.",
        "가격 대비 괜찮은 것 같아요. 재구매 고려 중입니다.",
        "피부 진정에 확실히 도움이 돼요. 다만 용량이 조금 적어요.",
        "순하고 자극 없이 사용할 수 있어서 좋아요.",
        "텍스처가 가벼워서 여름에도 부담 없이 쓸 수 있을 것 같아요.",
        "기대했던 것만큼은 아니지만 꽤 괜찮은 제품이에요.",
        "비건 제품 중에서는 상당히 만족스러운 편이에요.",
        "사용감은 좋은데 효과가 나타나기까지 시간이 좀 걸려요.",
        "포장이 꼼꼼하고 제품 자체도 괜찮아요. 무난하게 좋습니다.",
    ],
    3: [
        "보통이에요. 특별히 좋지도 나쁘지도 않아요.",
        "효과를 잘 모르겠어요. 좀 더 써봐야 할 것 같아요.",
        "성분은 좋은데 제 피부에는 큰 변화가 없네요.",
        "기대가 커서 그런지 약간 아쉽습니다.",
        "가격에 비해 용량이 좀 적은 것 같아요.",
        "무난한 제품이에요. 엄청 좋다는 느낌은 아니에요.",
        "나쁘진 않은데 재구매까지는 모르겠어요.",
        "흡수는 잘 되는데 보습 지속력이 좀 부족해요.",
    ],
    2: [
        "기대에 미치지 못했어요. 효과가 미미합니다.",
        "제 피부에는 안 맞는 것 같아요. 좀 따가웠어요.",
        "용량 대비 가격이 좀 비싼 느낌이에요.",
        "향이 너무 강해서 호불호가 갈릴 것 같아요.",
        "발림성은 괜찮은데 흡수가 너무 느려요.",
        "기대했는데 별로였어요. 다른 제품 찾아볼게요.",
    ],
    1: [
        "피부에 안 맞아서 트러블이 났어요. 환불 요청합니다.",
        "전혀 효과가 없어요. 실망입니다.",
        "냄새가 이상하고 질감도 안 좋아요.",
        "배송은 빨랐지만 제품이 기대 이하예요.",
    ],
}

# 구매한 유저-상품 조합에서 리뷰 생성
# 구매 이력이 있는 유저만 리뷰 가능
purchased_pairs = set()
for oi in order_items:
    order_obj = next((o for o in orders if o["id"] == oi["order_id"]), None)
    if order_obj and order_obj["status"] != "cancelled":
        purchased_pairs.add((order_obj["user_id"], oi["product_id"]))

purchased_pairs = list(purchased_pairs)
random.shuffle(purchased_pairs)

reviews = []
review_pairs_used = set()
review_count = 0

while review_count < 500 and purchased_pairs:
    user_id, product_id = purchased_pairs.pop()
    pair_key = (user_id, product_id)
    if pair_key in review_pairs_used:
        continue
    review_pairs_used.add(pair_key)

    rating = random.choices([1, 2, 3, 4, 5], weights=RATING_WEIGHTS)[0]
    content = random.choice(REVIEW_POOL[rating])

    # 리뷰 작성일 = 주문일 + 3~30일
    user_orders = [o for o in orders if o["user_id"] == user_id and o["status"] != "cancelled"]
    if user_orders:
        ref_order = random.choice(user_orders)
        review_date = datetime.fromisoformat(ref_order["ordered_at"]) + timedelta(days=random.randint(3, 30))
        if review_date > END_DATE:
            review_date = END_DATE - timedelta(days=random.randint(1, 7))
    else:
        review_date = random_kst_datetime(START_DATE + timedelta(days=30), END_DATE)

    reviews.append({
        "id": uuid4(),
        "user_id": user_id,
        "product_id": product_id,
        "rating": rating,
        "content": content,
        "created_at": review_date.isoformat(),
    })
    review_count += 1

reviews_df = pd.DataFrame(reviews)

# 평점 분포 확인
rating_dist = reviews_df["rating"].value_counts().sort_index()
print(f"  -> {len(reviews)}건 리뷰 생성 완료")
print(f"     평점 분포: {dict(rating_dist)}")

# ---------------------------------------------------------------------------
# 8. CSV 저장
# ---------------------------------------------------------------------------
print("[8/8] CSV 파일 저장 중...")
print(f"  -> 저장 경로: {CSV_DIR}")

# ingredients 컬럼은 리스트 -> Supabase text[] 호환 형태로 저장
# (CSV에서는 JSON 문자열 그대로 저장, Supabase 로딩 시 파싱)

csv_files = {
    "categories": cat_df,
    "products": prod_df,
    "users": user_df,
    "orders": order_df,
    "order_items": order_items_df,
    "sessions": sessions_df,
    "inventory": inventory_df,
    "reviews": reviews_df,
}

for table_name, df in csv_files.items():
    filepath = os.path.join(CSV_DIR, f"{table_name}.csv")
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"     {table_name}.csv -> {len(df)}건")

# ---------------------------------------------------------------------------
# 요약 통계
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("LUNA Shop 목업 데이터 생성 완료!")
print("=" * 60)
print()
print(f"  기간: {START_DATE.date()} ~ {END_DATE.date()} (12개월)")
print(f"  시간대: Asia/Seoul (KST, UTC+9)")
print(f"  Seed: {SEED}")
print()
print("  테이블별 건수:")
print(f"    categories:  {len(categories):>8,}건")
print(f"    products:    {len(products):>8,}건  (할인 상품 {len(sale_product_ids)}개)")
print(f"    users:       {len(users):>8,}건")
print(f"    orders:      {len(orders):>8,}건")
print(f"    order_items: {len(order_items):>8,}건  (주문당 평균 {len(order_items)/len(orders):.1f}개)")
print(f"    sessions:    {len(sessions_events):>8,}건  (이벤트)")
print(f"    inventory:   {len(inventory_records):>8,}건")
print(f"    reviews:     {len(reviews):>8,}건")
print()

# 매출 통계
paid_orders = [o for o in orders if o["status"] != "cancelled"]
total_gmv = sum(o["total_amount"] for o in paid_orders)
avg_order_value = total_gmv / len(paid_orders) if paid_orders else 0
print(f"  매출 통계:")
print(f"    총 GMV: {total_gmv:>15,}원")
print(f"    유효 주문: {len(paid_orders):>11,}건")
print(f"    평균 주문가: {avg_order_value:>12,.0f}원")
print(f"    VIP(상위 10%) 매출 비중: {vip_pct:.1f}%")
print()

# 퍼널 통계
print(f"  퍼널 전환율 (세션 기준):")
ss = funnel_counts.get("session_start", 0)
pv = funnel_counts.get("product_view", 0)
atc = funnel_counts.get("add_to_cart", 0)
co = funnel_counts.get("checkout_start", 0)
pu = funnel_counts.get("purchase", 0)
print(f"    Visit -> ProductView:   {pv/ss*100:.1f}% ({ss} -> {pv})")
print(f"    ProductView -> ATC:     {atc/pv*100:.1f}% ({pv} -> {atc})" if pv > 0 else "    ProductView -> ATC: N/A")
print(f"    ATC -> Checkout:        {co/atc*100:.1f}% ({atc} -> {co})" if atc > 0 else "    ATC -> Checkout: N/A")
print(f"    Checkout -> Purchase:   {pu/co*100:.1f}% ({co} -> {pu})" if co > 0 else "    Checkout -> Purchase: N/A")
print(f"    전체 전환율 (Visit->Purchase): {pu/ss*100:.1f}%" if ss > 0 else "")
print()
print(f"  CSV 파일: {CSV_DIR}")
print("=" * 60)
