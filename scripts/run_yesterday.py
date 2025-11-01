import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
from dotenv import load_dotenv


def compute_yesterday(date_format: str = "%Y-%m-%d") -> str:
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    return yesterday.strftime(date_format)


def main():
    # Optional args:
    #   1) config path (default: project configs/production_config.json)
    #   2) date (YYYY-MM-DD). If omitted, use yesterday.
    project_root = Path(__file__).resolve().parents[1]
    default_config = project_root / "configs" / "production_config.json"

    # Load environment variables from .env file (or .env.example as fallback)
    env_file = project_root / ".env"
    env_example_file = project_root / ".env.example"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from: {env_file}")
    elif env_example_file.exists():
        load_dotenv(env_example_file)
        print(f"⚠️  Loaded environment variables from .env.example (consider creating .env file): {env_example_file}")
    else:
        print(f"⚠️  No .env or .env.example file found in {project_root}")

    config_path = sys.argv[1] if len(sys.argv) > 1 else str(default_config)
    run_date = sys.argv[2] if len(sys.argv) > 2 else compute_yesterday()

    # Ensure absolute config path for clarity
    config_path = str(Path(config_path).resolve())

    # Optional trading calendar check
    # Set FORCE_RUN_NON_TRADING=1 to bypass skipping on non-trading days
    calendar_path = project_root / "data" / "trading_calendar" / "us_trading_days_2025Q4.json"
    if calendar_path.exists():
        try:
            with open(calendar_path, "r", encoding="utf-8") as f:
                calendar = json.load(f)
            trading_days = set(calendar.get("trading_days", []))
            if os.getenv("FORCE_RUN_NON_TRADING", "0") not in ("1", "true", "True"):
                if run_date not in trading_days:
                    print(f"Skip: {run_date} is not in trading calendar {calendar_path}")
                    return
        except Exception as e:
            print(f"Warning: failed to read trading calendar {calendar_path}: {e}")

    # Export date overrides for main.py to pick up
    os.environ["INIT_DATE"] = run_date
    os.environ["END_DATE"] = run_date

    # Import and run the project main
    sys.path.insert(0, str(project_root))
    import asyncio
    import main_parallel as project_main

    print(f"Running for date: {run_date}")
    print(f"Using config: {config_path}")
    asyncio.run(project_main.main(config_path))


if __name__ == "__main__":
    main()


