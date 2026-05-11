import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'backend' / 'ad_quality.db'}")
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import SessionLocal
from app.models import Impression
from app.services.attribution import record_click


def main() -> None:
    db = SessionLocal()
    try:
        impression = db.query(Impression).first()
        if impression is None:
            raise RuntimeError("No impression found. Run seed_data.py and generate_traffic.py first.")
        for _ in range(5):
            record_click(db, impression.id)
        print("Injected repeated clicks for duplicate-click and high-CTR quality checks.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
