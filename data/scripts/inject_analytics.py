"""
LUNA Shop - Amplitude / Mixpanel 이벤트 주입 스크립트
=====================================================
sessions.csv의 이벤트 데이터를 Amplitude HTTP API V2 / Mixpanel Import API로 전송

사용법:
  python inject_analytics.py                    # Amplitude + Mixpanel 모두
  python inject_analytics.py --amplitude-only   # Amplitude만
  python inject_analytics.py --mixpanel-only    # Mixpanel만
  python inject_analytics.py --dry-run          # 전송 없이 검증만
  python inject_analytics.py --limit 100        # 처음 100건만

필요 환경변수 (.env):
  # Amplitude
  AMPLITUDE_API_KEY=...

  # Mixpanel
  MIXPANEL_PROJECT_TOKEN=...
  MIXPANEL_PROJECT_ID=...
  MIXPANEL_SERVICE_ACCOUNT_USERNAME=...
  MIXPANEL_SERVICE_ACCOUNT_SECRET=...
"""

import os
import sys
import csv
import json
import time
import argparse
from datetime import datetime

import requests
from dotenv import load_dotenv

# ─── 설정 ───────────────────────────────────────────────

load_dotenv()

AMPLITUDE_API_KEY = os.getenv("AMPLITUDE_API_KEY")
MIXPANEL_PROJECT_TOKEN = os.getenv("MIXPANEL_PROJECT_TOKEN")
MIXPANEL_PROJECT_ID = os.getenv("MIXPANEL_PROJECT_ID")
MIXPANEL_SA_USER = os.getenv("MIXPANEL_SERVICE_ACCOUNT_USERNAME")
MIXPANEL_SA_SECRET = os.getenv("MIXPANEL_SERVICE_ACCOUNT_SECRET")

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "csv", "sessions.csv")
BATCH_SIZE = 2000  # 두 API 모두 배치 지원

# Amplitude HTTP API V2
AMPLITUDE_URL = "https://api2.amplitude.com/2/httpapi"

# Mixpanel Import API
MIXPANEL_IMPORT_URL = "https://api.mixpanel.com/import"


# ─── 이벤트 변환 ────────────────────────────────────────

def parse_iso_to_ms(iso_str: str) -> int:
    """ISO 8601 → Unix milliseconds"""
    # "2026-03-14T20:48:56.661147+09:00" 형식 처리
    dt = datetime.fromisoformat(iso_str)
    return int(dt.timestamp() * 1000)


def parse_iso_to_sec(iso_str: str) -> int:
    """ISO 8601 → Unix seconds"""
    dt = datetime.fromisoformat(iso_str)
    return int(dt.timestamp())


def csv_to_amplitude_event(row: dict) -> dict:
    """CSV 행 → Amplitude 이벤트 포맷"""
    event_params = {}
    if row.get("event_params"):
        try:
            event_params = json.loads(row["event_params"])
        except (json.JSONDecodeError, TypeError):
            pass

    event = {
        "event_type": row["event_name"],
        "time": parse_iso_to_ms(row["created_at"]),
        "session_id": hash(row["session_id"]) & 0xFFFFFFFF,  # Amplitude uses int session_id
        "event_properties": {
            **event_params,
            "page_path": row.get("page_path", ""),
            "referrer": row.get("referrer", ""),
        },
        "user_properties": {
            "utm_source": row.get("utm_source", ""),
            "utm_medium": row.get("utm_medium", ""),
            "utm_campaign": row.get("utm_campaign", ""),
        },
        "platform": "Web",
        "device_type": row.get("device_type", "desktop"),
    }

    # user_id (로그인 유저) 또는 device_id (익명)
    if row.get("user_id"):
        event["user_id"] = row["user_id"]
    else:
        event["device_id"] = f"anon_{row['session_id']}"

    return event


def csv_to_mixpanel_event(row: dict) -> dict:
    """CSV 행 → Mixpanel Import API 포맷"""
    event_params = {}
    if row.get("event_params"):
        try:
            event_params = json.loads(row["event_params"])
        except (json.JSONDecodeError, TypeError):
            pass

    properties = {
        "time": parse_iso_to_sec(row["created_at"]),
        "$insert_id": row["id"],  # 중복 방지용 고유 ID
        "session_id": row["session_id"],
        "page_path": row.get("page_path", ""),
        "referrer": row.get("referrer", ""),
        "device_type": row.get("device_type", "desktop"),
        "utm_source": row.get("utm_source", ""),
        "utm_medium": row.get("utm_medium", ""),
        "utm_campaign": row.get("utm_campaign", ""),
        **event_params,
    }

    # distinct_id: 로그인 유저는 user_id, 익명은 session_id
    if row.get("user_id"):
        properties["distinct_id"] = row["user_id"]
    else:
        properties["distinct_id"] = f"anon_{row['session_id']}"

    # token 필수
    properties["token"] = MIXPANEL_PROJECT_TOKEN

    return {
        "event": row["event_name"],
        "properties": properties,
    }


# ─── API 전송 ───────────────────────────────────────────

def send_amplitude_batch(events: list[dict]) -> bool:
    """Amplitude HTTP API V2로 배치 전송"""
    payload = {
        "api_key": AMPLITUDE_API_KEY,
        "events": events,
    }

    try:
        resp = requests.post(
            AMPLITUDE_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code == 200:
            return True
        else:
            print(f"    Amplitude 오류 ({resp.status_code}): {resp.text[:200]}")
            return False
    except requests.RequestException as e:
        print(f"    Amplitude 요청 실패: {e}")
        return False


def send_mixpanel_batch(events: list[dict]) -> bool:
    """Mixpanel Import API로 배치 전송"""
    try:
        resp = requests.post(
            MIXPANEL_IMPORT_URL,
            json=events,
            auth=(MIXPANEL_SA_USER, MIXPANEL_SA_SECRET),
            headers={"Content-Type": "application/json"},
            params={"project_id": MIXPANEL_PROJECT_ID},
            timeout=30,
        )
        if resp.status_code == 200:
            body = resp.json()
            if body.get("num_records_imported", 0) > 0:
                return True
            # 일부 실패
            if body.get("failed_records"):
                print(f"    Mixpanel 일부 실패: {len(body['failed_records'])}건")
            return True
        else:
            print(f"    Mixpanel 오류 ({resp.status_code}): {resp.text[:200]}")
            return False
    except requests.RequestException as e:
        print(f"    Mixpanel 요청 실패: {e}")
        return False


# ─── 메인 ───────────────────────────────────────────────

def load_sessions(limit: int = 0) -> list[dict]:
    """sessions.csv 로드"""
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description="LUNA Shop 이벤트 → Amplitude/Mixpanel 주입")
    parser.add_argument("--amplitude-only", action="store_true", help="Amplitude만 전송")
    parser.add_argument("--mixpanel-only", action="store_true", help="Mixpanel만 전송")
    parser.add_argument("--dry-run", action="store_true", help="전송 없이 변환 검증만")
    parser.add_argument("--limit", type=int, default=0, help="전송할 이벤트 수 제한")
    args = parser.parse_args()

    send_amplitude = not args.mixpanel_only
    send_mixpanel = not args.amplitude_only

    # 환경변수 확인
    if send_amplitude and not AMPLITUDE_API_KEY:
        print("✗ AMPLITUDE_API_KEY 환경변수를 설정하세요.")
        if not args.mixpanel_only:
            send_amplitude = False

    if send_mixpanel and not all([MIXPANEL_PROJECT_TOKEN, MIXPANEL_PROJECT_ID, MIXPANEL_SA_USER, MIXPANEL_SA_SECRET]):
        print("✗ Mixpanel 환경변수를 설정하세요:")
        print("  MIXPANEL_PROJECT_TOKEN, MIXPANEL_PROJECT_ID,")
        print("  MIXPANEL_SERVICE_ACCOUNT_USERNAME, MIXPANEL_SERVICE_ACCOUNT_SECRET")
        if not args.amplitude_only:
            send_mixpanel = False

    if not send_amplitude and not send_mixpanel:
        print("✗ Amplitude 또는 Mixpanel 중 하나 이상의 환경변수를 설정하세요.")
        sys.exit(1)

    # CSV 로드
    print(f"sessions.csv 로딩...")
    rows = load_sessions(args.limit)
    total = len(rows)
    print(f"  {total}건 로드 완료")

    if args.dry_run:
        # 변환 검증만
        print(f"\n[DRY RUN] 이벤트 변환 검증")
        sample = rows[0]
        if send_amplitude:
            amp_event = csv_to_amplitude_event(sample)
            print(f"\nAmplitude 샘플:")
            print(json.dumps(amp_event, indent=2, ensure_ascii=False)[:500])
        if send_mixpanel:
            mp_event = csv_to_mixpanel_event(sample)
            print(f"\nMixpanel 샘플:")
            print(json.dumps(mp_event, indent=2, ensure_ascii=False)[:500])
        print(f"\n[DRY RUN] {total}건 변환 가능 확인")
        return

    start = datetime.now()

    # ── Amplitude 전송 ──
    if send_amplitude:
        print(f"\n{'='*50}")
        print(f"Amplitude 전송 시작 ({total}건, 배치={BATCH_SIZE})")
        print(f"{'='*50}")

        amp_success = 0
        amp_fail = 0

        for i in range(0, total, BATCH_SIZE):
            batch_rows = rows[i : i + BATCH_SIZE]
            events = [csv_to_amplitude_event(r) for r in batch_rows]

            if send_amplitude_batch(events):
                amp_success += len(events)
            else:
                amp_fail += len(events)

            pct = min(100, int((i + len(batch_rows)) / total * 100))
            print(f"  [{pct:3d}%] {i + len(batch_rows)}/{total}")

            # Rate limiting 방지
            if i + BATCH_SIZE < total:
                time.sleep(0.5)

        print(f"\nAmplitude 완료: 성공 {amp_success}, 실패 {amp_fail}")

    # ── Mixpanel 전송 ──
    if send_mixpanel:
        print(f"\n{'='*50}")
        print(f"Mixpanel 전송 시작 ({total}건, 배치={BATCH_SIZE})")
        print(f"{'='*50}")

        mp_success = 0
        mp_fail = 0

        for i in range(0, total, BATCH_SIZE):
            batch_rows = rows[i : i + BATCH_SIZE]
            events = [csv_to_mixpanel_event(r) for r in batch_rows]

            if send_mixpanel_batch(events):
                mp_success += len(events)
            else:
                mp_fail += len(events)

            pct = min(100, int((i + len(batch_rows)) / total * 100))
            print(f"  [{pct:3d}%] {i + len(batch_rows)}/{total}")

            # Rate limiting 방지
            if i + BATCH_SIZE < total:
                time.sleep(0.5)

        print(f"\nMixpanel 완료: 성공 {mp_success}, 실패 {mp_fail}")

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n전체 완료! ({elapsed:.1f}초)")


if __name__ == "__main__":
    main()
