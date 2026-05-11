from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


def campaign_metrics(db: Session, campaign_id: int) -> dict[str, float | int]:
    campaign = db.get(models.Campaign, campaign_id)
    if campaign is None:
        raise ValueError("campaign does not exist")

    aggregate = (
        db.query(
            func.coalesce(func.sum(models.CampaignMetricsHourly.impressions), 0),
            func.coalesce(func.sum(models.CampaignMetricsHourly.clicks), 0),
            func.coalesce(func.sum(models.CampaignMetricsHourly.conversions), 0),
            func.coalesce(func.sum(models.CampaignMetricsHourly.spend), 0.0),
        )
        .filter(models.CampaignMetricsHourly.campaign_id == campaign_id)
        .one()
    )
    impressions = int(aggregate[0])
    clicks = int(aggregate[1])
    conversions = int(aggregate[2])
    ctr = clicks / impressions if impressions else 0.0
    cvr = conversions / clicks if clicks else 0.0
    spend = round(float(aggregate[3]), 4)
    return {
        "campaign_id": campaign_id,
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "ctr": round(ctr, 4),
        "cvr": round(cvr, 4),
        "spend": spend,
        "remaining_budget": campaign.remaining_budget,
    }
