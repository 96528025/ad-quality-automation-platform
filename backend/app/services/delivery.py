from sqlalchemy.orm import Session

from app import models
from app.services.aggregation import increment_impression


def user_matches_campaign(user: models.User, campaign: models.Campaign) -> bool:
    return (
        campaign.status == models.CampaignStatus.active
        and campaign.remaining_budget >= campaign.bid_cpc
        and user.country == campaign.target_country
        and campaign.target_age_min <= user.age <= campaign.target_age_max
    )


def select_ad_for_user(db: Session, user: models.User) -> models.Ad | None:
    ads = db.query(models.Ad).join(models.Campaign).all()
    eligible_ads = [ad for ad in ads if user_matches_campaign(user, ad.campaign)]
    if not eligible_ads:
        return None
    return max(eligible_ads, key=lambda ad: (ad.campaign.bid_cpc, ad.campaign.id))


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
