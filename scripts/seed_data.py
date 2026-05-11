import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'backend' / 'ad_quality.db'}")
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import Base, SessionLocal, engine
from app.models import Ad, Campaign, CampaignStatus, User


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users = [
            User(country="US", age=24, device="ios", interests="sports,fitness"),
            User(country="US", age=31, device="android", interests="travel,shopping"),
            User(country="CA", age=29, device="ios", interests="gaming"),
        ]
        campaign = Campaign(
            advertiser_name="Nike",
            daily_budget=500,
            remaining_budget=500,
            bid_cpc=1.2,
            target_country="US",
            target_age_min=18,
            target_age_max=35,
            target_device="any",
            target_interests="sports,fitness",
            frequency_cap_per_day=10,
            pacing_enabled=False,
            status=CampaignStatus.active,
        )
        db.add_all(users + [campaign])
        db.flush()
        db.add(
            Ad(
                campaign_id=campaign.id,
                title="Running Shoes",
                landing_url="https://example.com/running-shoes",
                creative_url="https://example.com/creative/shoes.png",
                review_status="approved",
                predicted_ctr=0.08,
                quality_score=0.9,
            )
        )
        db.commit()
        print("Seeded users, campaign, and ad.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
