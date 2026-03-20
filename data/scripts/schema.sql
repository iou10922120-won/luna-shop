-- LUNA Shop Database Schema
-- Supabase (PostgreSQL)
-- Phase 3: 목업 데이터 생성용

-- ============================================================
-- 1. 테이블 생성
-- ============================================================

-- 카테고리
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 상품
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    sale_price INTEGER,
    category_id UUID REFERENCES categories(id),
    image_url TEXT,
    ingredients TEXT[],
    ingredient_details JSONB,  -- [{name, role, origin, grade}]
    is_vegan_certified BOOLEAN DEFAULT true,
    stock_quantity INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 유저
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    gender TEXT,
    birth_date DATE,
    signup_channel TEXT,       -- google / kakao
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 주문
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    order_number TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'paid',  -- pending/paid/shipped/delivered/cancelled
    total_amount INTEGER NOT NULL,
    discount_amount INTEGER DEFAULT 0,
    shipping_fee INTEGER DEFAULT 0,
    shipping_address JSONB,
    coupon_code TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    ordered_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 주문 상품
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price INTEGER NOT NULL,
    subtotal INTEGER NOT NULL
);

-- 장바구니
CREATE TABLE IF NOT EXISTS cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- 리뷰
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 세션/이벤트 로그
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    user_id UUID REFERENCES users(id),  -- NULL for anonymous
    event_name TEXT NOT NULL,
    event_params JSONB,
    page_path TEXT,
    referrer TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    device_type TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

-- 재고 변동 이력
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    change_type TEXT NOT NULL,  -- inbound/sale/return/adjust
    quantity_change INTEGER NOT NULL,
    quantity_after INTEGER NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

-- ============================================================
-- 2. 인덱스 (대시보드 성능 최적화)
-- ============================================================

-- orders: 유저별 주문 조회, 날짜별 매출 집계
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);
CREATE INDEX idx_orders_status ON orders(status);

-- order_items: 주문별/상품별 조회
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- sessions: 이벤트 분석, 퍼널
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_event_name ON sessions(event_name);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

-- inventory: 상품별 재고 추적
CREATE INDEX idx_inventory_product_id ON inventory(product_id);
CREATE INDEX idx_inventory_created_at ON inventory(created_at);

-- reviews: 상품별 리뷰
CREATE INDEX idx_reviews_product_id ON reviews(product_id);

-- products: 카테고리별 조회
CREATE INDEX idx_products_category_id ON products(category_id);

-- ============================================================
-- 3. 요약 테이블 (대시보드 성능용)
-- ============================================================

-- 일별 매출 요약
CREATE TABLE IF NOT EXISTS daily_sales_summary (
    date DATE PRIMARY KEY,
    total_orders INTEGER DEFAULT 0,
    total_revenue INTEGER DEFAULT 0,
    total_items_sold INTEGER DEFAULT 0,
    avg_order_value INTEGER DEFAULT 0,
    unique_buyers INTEGER DEFAULT 0
);

-- 일별 퍼널 요약
CREATE TABLE IF NOT EXISTS funnel_daily (
    date DATE NOT NULL,
    step TEXT NOT NULL,  -- visit/product_view/add_to_cart/checkout_start/purchase
    session_count INTEGER DEFAULT 0,
    PRIMARY KEY (date, step)
);

-- 월별 코호트 리텐션
CREATE TABLE IF NOT EXISTS monthly_cohort (
    cohort_month DATE NOT NULL,    -- 가입 월 (YYYY-MM-01)
    month_offset INTEGER NOT NULL,  -- M0, M1, M2...
    cohort_size INTEGER DEFAULT 0,  -- 해당 코호트 가입자 수
    retained_users INTEGER DEFAULT 0,
    retention_rate NUMERIC(5,2) DEFAULT 0,
    PRIMARY KEY (cohort_month, month_offset)
);

-- 유저별 RFM
CREATE TABLE IF NOT EXISTS rfm_segments (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    last_purchase_date DATE,
    recency_days INTEGER,
    frequency INTEGER,
    monetary INTEGER,
    r_score INTEGER CHECK (r_score BETWEEN 1 AND 5),
    f_score INTEGER CHECK (f_score BETWEEN 1 AND 5),
    m_score INTEGER CHECK (m_score BETWEEN 1 AND 5),
    rfm_segment TEXT,  -- VIP/충성고객/신규유망/이탈위험/슬리퍼/할인사냥꾼
    calculated_at TIMESTAMPTZ DEFAULT now()
);

-- 상품별 성과
CREATE TABLE IF NOT EXISTS product_performance (
    product_id UUID PRIMARY KEY REFERENCES products(id),
    product_name TEXT,
    category TEXT,
    total_sold INTEGER DEFAULT 0,
    total_revenue INTEGER DEFAULT 0,
    avg_rating NUMERIC(3,2),
    review_count INTEGER DEFAULT 0,
    current_stock INTEGER DEFAULT 0,
    inventory_turnover NUMERIC(5,2),  -- 재고 회전율
    calculated_at TIMESTAMPTZ DEFAULT now()
);
