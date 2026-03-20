"""
LUNA Shop - Supabase 데이터 업로드 스크립트
==========================================
CSV 파일 → Supabase (PostgreSQL) 업로드
FK 의존 순서대로 삽입, 배치 처리

사용법:
  python load_to_supabase.py              # 전체 업로드
  python load_to_supabase.py --table users # 특정 테이블만
  python load_to_supabase.py --dry-run     # 실제 삽입 없이 검증만

필요 환경변수 (.env):
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_KEY=eyJ...  (service_role_key 권장)
"""

import os
import sys
import csv
import json
import argparse
from datetime import datetime

from dotenv import load_dotenv
from supabase import create_client, Client

# ─── 설정 ───────────────────────────────────────────────

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "csv")

BATCH_SIZE = 500  # Supabase REST API 배치 크기

# FK 의존 순서 (부모 → 자식)
TABLE_ORDER = [
    "categories",
    "products",
    "users",
    "orders",
    "order_items",
    "cart_items",
    "reviews",
    "sessions",
    "inventory",
]

# 각 테이블의 CSV 컬럼 → 타입 변환 규칙
COLUMN_TYPES = {
    "categories": {
        "display_order": int,
    },
    "products": {
        "price": int,
        "sale_price": "nullable_int",
        "ingredients": "json",
        "ingredient_details": "json",
        "is_vegan_certified": "bool",
        "stock_quantity": int,
    },
    "users": {},
    "orders": {
        "total_amount": int,
        "discount_amount": int,
        "shipping_fee": int,
        "shipping_address": "json",
    },
    "order_items": {
        "quantity": int,
        "unit_price": int,
        "subtotal": int,
    },
    "cart_items": {
        "quantity": int,
    },
    "reviews": {
        "rating": int,
    },
    "sessions": {
        "event_params": "json",
    },
    "inventory": {
        "quantity_change": int,
        "quantity_after": int,
    },
}


# ─── 유틸 ───────────────────────────────────────────────

def convert_value(value: str, type_hint) -> any:
    """CSV 문자열을 적절한 Python 타입으로 변환"""
    if value == "" or value is None:
        return None

    if type_hint == int:
        # "23100.0" 같은 float 문자열 처리
        return int(float(value))
    elif type_hint == "nullable_int":
        if value == "" or value is None:
            return None
        return int(float(value))
    elif type_hint == "json":
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    elif type_hint == "bool":
        return value.lower() in ("true", "1", "yes")
    else:
        return value


def read_csv_rows(table_name: str) -> list[dict]:
    """CSV 파일을 읽어서 타입 변환된 dict 리스트 반환"""
    csv_path = os.path.join(CSV_DIR, f"{table_name}.csv")
    if not os.path.exists(csv_path):
        print(f"  ⚠ {csv_path} 파일 없음 — 건너뜀")
        return []

    type_map = COLUMN_TYPES.get(table_name, {})
    rows = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            converted = {}
            for key, value in row.items():
                if key in type_map:
                    converted[key] = convert_value(value, type_map[key])
                elif value == "":
                    converted[key] = None
                else:
                    converted[key] = value
            rows.append(converted)

    return rows


def upload_table(supabase: Client, table_name: str, rows: list[dict], dry_run: bool = False):
    """테이블에 배치 INSERT"""
    total = len(rows)
    if total == 0:
        print(f"  {table_name}: 데이터 없음")
        return

    print(f"  {table_name}: {total}건 업로드 중...")

    if dry_run:
        print(f"    [DRY RUN] {total}건 검증 완료")
        return

    uploaded = 0
    errors = 0

    for i in range(0, total, BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        try:
            supabase.table(table_name).insert(batch).execute()
            uploaded += len(batch)
            pct = int(uploaded / total * 100)
            print(f"    {uploaded}/{total} ({pct}%)")
        except Exception as e:
            errors += len(batch)
            print(f"    ✗ 배치 {i//BATCH_SIZE + 1} 실패: {e}")
            # 개별 행 삽입 시도
            for row in batch:
                try:
                    supabase.table(table_name).insert(row).execute()
                    uploaded += 1
                    errors -= 1
                except Exception as row_err:
                    print(f"      ✗ 행 실패 ({row.get('id', 'unknown')}): {row_err}")

    print(f"    완료: 성공 {uploaded}건, 실패 {errors}건")


# ─── 메인 ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LUNA Shop CSV → Supabase 업로드")
    parser.add_argument("--table", help="특정 테이블만 업로드 (예: users)")
    parser.add_argument("--dry-run", action="store_true", help="실제 삽입 없이 검증만")
    parser.add_argument("--clean", action="store_true", help="업로드 전 기존 데이터 삭제")
    args = parser.parse_args()

    # 환경변수 확인
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("✗ SUPABASE_URL, SUPABASE_KEY 환경변수를 설정하세요.")
        print("  .env 파일에 다음 내용을 추가하세요:")
        print("  SUPABASE_URL=https://xxx.supabase.co")
        print("  SUPABASE_KEY=eyJ... (service_role_key)")
        sys.exit(1)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Supabase 연결: {SUPABASE_URL}")

    # 업로드할 테이블 결정
    if args.table:
        if args.table not in TABLE_ORDER:
            print(f"✗ 알 수 없는 테이블: {args.table}")
            print(f"  사용 가능: {', '.join(TABLE_ORDER)}")
            sys.exit(1)
        tables = [args.table]
    else:
        tables = TABLE_ORDER

    # 기존 데이터 삭제 (역순 — FK 제약 때문)
    if args.clean:
        print("\n기존 데이터 삭제 중...")
        for table in reversed(tables):
            try:
                # Supabase: neq 필터로 전체 삭제
                supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                print(f"  {table}: 삭제 완료")
            except Exception as e:
                print(f"  {table}: 삭제 실패 — {e}")

    # 업로드
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}데이터 업로드 시작")
    print(f"CSV 경로: {os.path.abspath(CSV_DIR)}")
    print(f"배치 크기: {BATCH_SIZE}\n")

    start = datetime.now()

    for table in tables:
        rows = read_csv_rows(table)
        upload_table(supabase, table, rows, dry_run=args.dry_run)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n완료! ({elapsed:.1f}초)")

    if not args.dry_run:
        print("\n다음 단계: 요약 테이블 생성")
        print("  Supabase SQL Editor에서 build_summaries.sql 실행")


if __name__ == "__main__":
    main()
