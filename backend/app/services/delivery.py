from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.services.aggregation import increment_impression


def parse_csv_values(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def device_matches(user: models.User, campaign: models.Campaign) -> bool:
    return campaign.target_device.lower() in {"", "any"} or user.device.lower() == campaign.target_device.lower()


def interests_match(user: models.User, campaign: models.Campaign) -> bool:
    target_interests = parse_csv_values(campaign.target_interests)
    if not target_interests:
        return True
    user_interests = parse_csv_values(user.interests)
    return bool(user_interests.intersection(target_interests))


def frequency_cap_available(db: Session, user: models.User, campaign: models.Campaign) -> bool:
    day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    impressions_today = (
        db.query(func.count(models.Impression.id))
        .filter(
            models.Impression.user_id == user.id,
            models.Impression.campaign_id == campaign.id,
            models.Impression.created_at >= day_start,
        )
        .scalar()
    )
    return int(impressions_today or 0) < campaign.frequency_cap_per_day


def pacing_available(db: Session, campaign: models.Campaign) -> bool:
    if not campaign.pacing_enabled:
        return True

    now = datetime.utcnow()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_seconds = max((now - day_start).total_seconds(), 1)
    allowed_spend = campaign.daily_budget * (elapsed_seconds / timedelta(days=1).total_seconds())
    actual_spend = campaign.daily_budget - campaign.remaining_budget
    return actual_spend + campaign.bid_cpc <= allowed_spend


def user_matches_campaign(db: Session, user: models.User, campaign: models.Campaign) -> bool:
    return (
        campaign.status == models.CampaignStatus.active
        and campaign.remaining_budget >= campaign.bid_cpc
        and user.country == campaign.target_country
        and campaign.target_age_min <= user.age <= campaign.target_age_max
        and device_matches(user, campaign)
        and interests_match(user, campaign)
        and frequency_cap_available(db, user, campaign)
        and pacing_available(db, campaign)
    )


def ranking_score(ad: models.Ad) -> float:
    return round(ad.campaign.bid_cpc * ad.predicted_ctr * ad.quality_score, 6)


def select_ad_for_user(db: Session, user: models.User) -> models.Ad | None:
    ads = db.query(models.Ad).join(models.Campaign).all()
    eligible_ads = [
        ad
        for ad in ads
        if ad.review_status == models.ReviewStatus.approved and user_matches_campaign(db, user, ad.campaign)
    ]
    if not eligible_ads:
        return None
    return max(eligible_ads, key=lambda ad: (ranking_score(ad), ad.campaign.id, ad.id))


def deliver_ad(db: Session, user_id: int) -> tuple[models.Ad, models.Impression] | None:
    user = db.get(models.User, user_id)
    if user is None:
        return None

    ad = select_ad_for_user(db, user)
    if ad is None:
        return None

    impression = models.Impression(campaign_id=ad.campaign_id, ad_id=ad.id, user_id=user.id)
    db.add(impression)
    increment_impression(db, ad.campaign_id)
    db.commit()
    db.refresh(impression)
    db.refresh(ad)
    return ad, impression
