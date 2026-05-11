from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services.aggregation import increment_impression
from app.services.attribution import record_click, record_conversion


def ingest_event(
    db: Session,
    event_type: models.EventType,
    campaign_id: int | None = None,
    ad_id: int | None = None,
    user_id: int | None = None,
    impression_id: int | None = None,
    click_id: int | None = None,
    conversion_value: float | None = None,
    event_time: datetime | None = None,
) -> models.AdEvent:
    event = models.AdEvent(
        event_type=event_type,
        campaign_id=campaign_id,
        ad_id=ad_id,
        user_id=user_id,
        impression_id=impression_id,
        click_id=click_id,
        conversion_value=conversion_value,
        event_time=event_time or datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def process_event(db: Session, event: models.AdEvent) -> models.AdEvent:
    try:
        if event.event_type == models.EventType.impression:
            materialized_id = process_impression_event(db, event)
        elif event.event_type == models.EventType.click:
            materialized_id = process_click_event(db, event)
        elif event.event_type == models.EventType.conversion:
            materialized_id = process_conversion_event(db, event)
        else:
            raise ValueError("unsupported event type")
    except ValueError as exc:
        event.status = models.EventStatus.failed
        event.error_message = str(exc)
        event.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(event)
        return event

    event.status = models.EventStatus.processed
    event.materialized_id = materialized_id
    event.error_message = None
    event.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


def process_pending_events(db: Session, limit: int = 100) -> tuple[int, int]:
    events = (
        db.query(models.AdEvent)
        .filter(models.AdEvent.status == models.EventStatus.pending)
        .order_by(models.AdEvent.id)
        .limit(limit)
        .all()
    )
    processed = 0
    failed = 0
    for event in events:
        updated = process_event(db, event)
        if updated.status == models.EventStatus.processed:
            processed += 1
        else:
            failed += 1
    return processed, failed


def process_impression_event(db: Session, event: models.AdEvent) -> int:
    if event.campaign_id is None or event.ad_id is None or event.user_id is None:
        raise ValueError("impression event requires campaign_id, ad_id, and user_id")
    if db.get(models.Campaign, event.campaign_id) is None:
        raise ValueError("campaign does not exist")
    if db.get(models.Ad, event.ad_id) is None:
        raise ValueError("ad does not exist")
    if db.get(models.User, event.user_id) is None:
        raise ValueError("user does not exist")

    impression = models.Impression(
        campaign_id=event.campaign_id,
        ad_id=event.ad_id,
        user_id=event.user_id,
        created_at=event.event_time,
    )
    db.add(impression)
    increment_impression(db, event.campaign_id, event.event_time)
    db.flush()
    return impression.id


def process_click_event(db: Session, event: models.AdEvent) -> int:
    if event.impression_id is None:
        raise ValueError("click event requires impression_id")
    click = record_click(db, event.impression_id)
    return click.id


def process_conversion_event(db: Session, event: models.AdEvent) -> int:
    if event.click_id is None or event.conversion_value is None:
        raise ValueError("conversion event requires click_id and conversion_value")
    conversion = record_conversion(db, event.click_id, event.conversion_value, event.event_time)
    return conversion.id
