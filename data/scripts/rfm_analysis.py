"""
LUNA Shop — RFM 세그먼테이션 분석
CSV 데이터 기반 고객 세그먼트 분류 + 결과 CSV 출력
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 데이터 로드 ────────────────────────────────────────────
users = pd.read_csv(CSV_DIR / "users.csv")
orders = pd.read_csv(CSV_DIR / "orders.csv")

# 날짜 변환
orders["ordered_at"] = pd.to_datetime(orders["ordered_at"])

# 취소 주문 제외
orders = orders[orders["status"] != "cancelled"]

# 기준일 (데이터의 최대 날짜 + 1일)
reference_date = orders["ordered_at"].max() + pd.Timedelta(days=1)

# ── RFM 계산 ───────────────────────────────────────────────
rfm = orders.groupby("user_id").agg(
    last_purchase=("ordered_at", "max"),
    frequency=("id", "nunique"),
    monetary=("total_amount", "sum"),
).reset_index()

rfm["recency_days"] = (reference_date - rfm["last_purchase"]).dt.days

# ── RFM 점수 부여 (1-5) ───────────────────────────────────
def r_score(days):
    if days <= 14: return 5
    if days <= 30: return 4
    if days <= 60: return 3
    if days <= 90: return 2
    return 1

def f_score(freq):
    if freq >= 10: return 5
    if freq >= 7: return 4
    if freq >= 4: return 3
    if freq >= 2: return 2
    return 1

def m_score(amount):
    if amount >= 500000: return 5
    if amount >= 300000: return 4
    if amount >= 150000: return 3
    if amount >= 50000: return 2
    return 1

rfm["R"] = rfm["recency_days"].apply(r_score)
rfm["F"] = rfm["frequency"].apply(f_score)
rfm["M"] = rfm["monetary"].apply(m_score)
rfm["RFM_sum"] = rfm["R"] + rfm["F"] + rfm["M"]

# ── 세그먼트 분류 ──────────────────────────────────────────
def assign_segment(row):
    r, f, m = row["R"], row["F"], row["M"]
    if r >= 4 and f >= 4 and m >= 4:
        return "VIP"
    if r >= 3 and f >= 3:
        return "충성고객"
    if r >= 4 and f <= 2:
        return "신규유망"
    if r <= 2 and f >= 3:
        return "이탈위험"
    if r <= 2 and f <= 2:
        return "슬리퍼"
    if m <= 2 and f >= 3:
        return "할인사냥꾼"
    return "일반"

rfm["segment"] = rfm.apply(assign_segment, axis=1)

# ── 유저 정보 조인 ─────────────────────────────────────────
rfm = rfm.merge(users[["id", "name", "email", "signup_channel"]], left_on="user_id", right_on="id", how="left")
rfm.drop(columns=["id"], inplace=True)

# ── 결과 출력 ──────────────────────────────────────────────
# 1) 고객별 RFM 상세
rfm_output = rfm[[
    "user_id", "name", "email", "signup_channel",
    "last_purchase", "recency_days", "frequency", "monetary",
    "R", "F", "M", "RFM_sum", "segment"
]].sort_values("monetary", ascending=False)

rfm_output.to_csv(OUTPUT_DIR / "rfm_customers.csv", index=False, encoding="utf-8-sig")

# 2) 세그먼트 요약
segment_summary = rfm.groupby("segment").agg(
    고객수=("user_id", "count"),
    평균구매액=("monetary", "mean"),
    평균구매횟수=("frequency", "mean"),
    평균경과일=("recency_days", "mean"),
).round(0).reset_index()

segment_summary["고객비율(%)"] = (segment_summary["고객수"] / segment_summary["고객수"].sum() * 100).round(1)
segment_summary = segment_summary.sort_values("평균구매액", ascending=False)
segment_summary.to_csv(OUTPUT_DIR / "rfm_segment_summary.csv", index=False, encoding="utf-8-sig")

# ── 콘솔 출력 ──────────────────────────────────────────────
print("=" * 60)
print("LUNA Shop — RFM 세그먼테이션 결과")
print("=" * 60)
print(f"\n기준일: {reference_date.strftime('%Y-%m-%d')}")
print(f"분석 대상: {len(rfm)}명 (1회 이상 구매 고객)\n")
print("── 세그먼트별 요약 ──")
print(segment_summary.to_string(index=False))
print(f"\n결과 저장:")
print(f"  → {OUTPUT_DIR / 'rfm_customers.csv'}")
print(f"  → {OUTPUT_DIR / 'rfm_segment_summary.csv'}")
