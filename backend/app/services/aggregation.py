from datetime import datetime

from sqlalchemy.orm import Session

from app import models


def hour_bucket(value: datetime | None = None) -> datetime:
    event_time = value or datetime.utcnow()
    return event_time.replace(minute=0, second=0, microsecond=0)


def get_or_create_hourly_metrics(
    db: Session,
    campaign_id: int,
    event_time: datetime | None = None,
) -> models.CampaignMetricsHourly:
    bucket_start = hour_bucket(event_time)
    row = (
        db.query(models.CampaignMetricsHourly)
        .filter(
            models.CampaignMetricsHourly.campaign_id == campaign_id,
            models.CampaignMetricsHourly.bucket_start == bucket_start,
        )
        .first()
    )
    if row is not None:
        return row

    row = models.CampaignMetricsHourly(campaign_id=campaign_id, bucket_start=bucket_start)
    db.add(row)
    db.flush()
    return row


def increment_impression(db: Session, campaign_id: int, event_time: datetime | None = None) -> None:
    row = get_or_create_hourly_metrics(db, campaign_id, event_time)
    row.impressions += 1


def increment_click(db: Session, campaign_id: int, spend: float, event_time: datetime | None = None) -> None:
    row = get_or_create_hourly_metrics(db, campaign_id, event_time)
    row.clicks += 1
    row.spend = round(row.spend + spend, 4)


def increment_conversion(
    db: Session,
    campaign_id: int,
    conversion_value: float,
    event_time: datetime | None = None,
) -> None:
    row = get_or_create_hourly_metrics(db, campaign_id, event_time)
    row.conversions += 1
    row.conversion_value = round(row.conversion_value + conversion_value, 4)
