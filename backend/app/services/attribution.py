from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services.aggregation import increment_click, increment_conversion

ATTRIBUTION_WINDOW_DAYS = 7


def record_click(db: Session, impression_id: int) -> models.Click:
    impression = db.get(models.Impression, impression_id)
    if impression is None:
        raise ValueError("impression does not exist")

    campaign = db.get(models.Campaign, impression.campaign_id)
    if campaign is None or campaign.remaining_budget < campaign.bid_cpc:
        raise ValueError("campaign budget is not available")

    click = models.Click(
        impression_id=impression.id,
        campaign_id=impression.campaign_id,
        ad_id=impression.ad_id,
        user_id=impression.user_id,
    )
    campaign.remaining_budget = round(campaign.remaining_budget - campaign.bid_cpc, 4)
    db.add(click)
    increment_click(db, campaign.id, campaign.bid_cpc)
    db.commit()
    db.refresh(click)
    return click


def record_conversion(
    db: Session,
    click_id: int,
    conversion_value: float,
    created_at: datetime | None = None,
) -> models.Conversion:
    click = db.get(models.Click, click_id)
    if click is None:
        raise ValueError("click does not exist")

    event_time = created_at or datetime.utcnow()
    if event_time - click.created_at > timedelta(days=ATTRIBUTION_WINDOW_DAYS):
        raise ValueError("conversion is outside attribution window")

    existing = db.query(models.Conversion).filter(models.Conversion.click_id == click_id).first()
    if existing is not None:
        raise ValueError("duplicate conversion for click")

    conversion = models.Conversion(
        click_id=click.id,
        campaign_id=click.campaign_id,
        user_id=click.user_id,
        conversion_value=conversion_value,
        created_at=event_time,
    )
    db.add(conversion)
    increment_conversion(db, click.campaign_id, conversion_value, event_time)
    db.commit()
    db.refresh(conversion)
    return conversion
