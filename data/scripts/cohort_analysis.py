"""
LUNA Shop — 코호트 리텐션 분석
가입 월 기준 코호트별 월간 구매 리텐션 + 결과 CSV 출력
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 데이터 로드 ────────────────────────────────────────────
users = pd.read_csv(CSV_DIR / "users.csv")
orders = pd.read_csv(CSV_DIR / "orders.csv")

users["created_at"] = pd.to_datetime(users["created_at"])
orders["ordered_at"] = pd.to_datetime(orders["ordered_at"])

# 취소 주문 제외
orders = orders[orders["status"] != "cancelled"]

# ── 코호트 설정 ────────────────────────────────────────────
# 유저별 가입 월
users["cohort_month"] = users["created_at"].dt.to_period("M")

# 주문별 주문 월
orders["order_month"] = orders["ordered_at"].dt.to_period("M")

# 유저-주문 조인
user_orders = orders.merge(
    users[["id", "cohort_month"]],
    left_on="user_id",
    right_on="id",
    how="inner",
    suffixes=("", "_user")
)

# 월 오프셋 계산
user_orders["month_offset"] = (
    user_orders["order_month"].astype(int) - user_orders["cohort_month"].astype(int)
)

# ── 코호트 테이블 계산 ─────────────────────────────────────
# 코호트별 크기
cohort_sizes = users.groupby("cohort_month")["id"].nunique().reset_index()
cohort_sizes.columns = ["cohort_month", "cohort_size"]

# 코호트 × 오프셋별 유니크 유저 수
retention = (
    user_orders[user_orders["month_offset"] >= 0]
    .groupby(["cohort_month", "month_offset"])["user_id"]
    .nunique()
    .reset_index()
)
retention.columns = ["cohort_month", "month_offset", "retained_users"]

# 코호트 크기 조인
retention = retention.merge(cohort_sizes, on="cohort_month")
retention["retention_rate"] = (retention["retained_users"] / retention["cohort_size"] * 100).round(1)

# ── 결과 1: 상세 데이터 (long format — Tableau용) ──────────
retention_long = retention.copy()
retention_long["cohort_month"] = retention_long["cohort_month"].astype(str)
retention_long.to_csv(OUTPUT_DIR / "cohort_retention_long.csv", index=False, encoding="utf-8-sig")

# ── 결과 2: 피벗 테이블 (wide format — 시각적 확인용) ──────
retention_pivot = retention.pivot_table(
    index="cohort_month",
    columns="month_offset",
    values="retention_rate",
    aggfunc="first"
)
retention_pivot.columns = [f"M{int(c)}" for c in retention_pivot.columns]
retention_pivot.index = retention_pivot.index.astype(str)

# 코호트 크기 추가
sizes = cohort_sizes.set_index("cohort_month")["cohort_size"]
sizes.index = sizes.index.astype(str)
retention_pivot.insert(0, "코호트크기", sizes)

retention_pivot.to_csv(OUTPUT_DIR / "cohort_retention_pivot.csv", encoding="utf-8-sig")

# ── 콘솔 출력 ──────────────────────────────────────────────
print("=" * 60)
print("LUNA Shop — 코호트 리텐션 분석 결과")
print("=" * 60)
print(f"\n분석 대상: {len(users)}명, {len(orders)}건 주문\n")
print("── 코호트 리텐션 테이블 (%) ──")
print(retention_pivot.to_string())
print(f"\n결과 저장:")
print(f"  → {OUTPUT_DIR / 'cohort_retention_long.csv'} (Tableau용)")
print(f"  → {OUTPUT_DIR / 'cohort_retention_pivot.csv'} (확인용)")
