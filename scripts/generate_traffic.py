import os
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'backend' / 'ad_quality.db'}")
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import SessionLocal
from app.models import User
from app.services.attribution import record_click, record_conversion
from app.services.delivery import deliver_ad


def main(events: int = 100) -> None:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            raise RuntimeError("No users found. Run scripts/seed_data.py first.")

        impressions = clicks = conversions = 0
        for _ in range(events):
            user = random.choice(users)
            delivery = deliver_ad(db, user.id)
            if delivery is None:
                continue
            _, impression = delivery
            impressions += 1
            if random.random() < 0.08:
                click = record_click(db, impression.id)
                clicks += 1
                if random.random() < 0.12:
                    record_conversion(db, click.id, round(random.uniform(20, 200), 2))
                    conversions += 1
        print(f"Generated {impressions} impressions, {clicks} clicks, {conversions} conversions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
