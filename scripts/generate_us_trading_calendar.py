import json
from datetime import date, timedelta
from pathlib import Path


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def build_us_trading_days_q4_2025():
    start = date(2025, 10, 1)
    end = date(2025, 12, 31)
    # NYSE/Nasdaq are closed on these two federal market holidays in Q4 2025
    market_holidays = {
        date(2025, 11, 27),  # Thanksgiving Day
        date(2025, 12, 25),  # Christmas Day
    }
    trading_days = []
    for d in daterange(start, end):
        if d.weekday() >= 5:
            continue  # skip weekends
        if d in market_holidays:
            continue
        trading_days.append(d.strftime("%Y-%m-%d"))
    return trading_days


def main():
    project_root = Path(__file__).resolve().parents[1]
    out_dir = project_root / "data" / "trading_calendar"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "us_trading_days_2025Q4.json"

    trading_days = build_us_trading_days_q4_2025()
    payload = {
        "market": "US",
        "name": "NYSE/NASDAQ",
        "range": {"start": "2025-10-01", "end": "2025-12-31"},
        "holidays": ["2025-11-27", "2025-12-25"],
        "notes": "Weekdays excluding Thanksgiving and Christmas for Q4 2025. Day-after Thanksgiving and Christmas Eve are trading days (early close not modeled).",
        "trading_days": trading_days,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(trading_days)} trading days to {out_path}")


if __name__ == "__main__":
    main()


