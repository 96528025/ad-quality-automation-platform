from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models

SUSPICIOUS_RISK_THRESHOLD = 40
INVALID_RISK_THRESHOLD = 70


def score_click_event(db: Session, event: models.AdEvent) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if not event.user_agent:
        score += 10
        reasons.append("missing_user_agent")

    if event.ip_address and recent_click_events_for_ip(db, event.ip_address) >= 20:
        score += 40
        reasons.append("high_ip_click_volume")

    if event.device_id and recent_click_events_for_device(db, event.device_id) >= 15:
        score += 30
        reasons.append("high_device_click_volume")

    if event.impression_id is not None:
        impression = db.get(models.Impression, event.impression_id)
        if impression is not None and repeated_clicks_for_user_ad(db, impression.user_id, impression.ad_id) >= 3:
            score += 30
            reasons.append("repeated_user_ad_clicks")

    return min(score, 100), reasons


def recent_click_events_for_ip(db: Session, ip_address: str) -> int:
    since = datetime.utcnow() - timedelta(hours=1)
    return int(
        db.query(func.count(models.AdEvent.id))
        .filter(
            models.AdEvent.event_type == models.EventType.click,
            models.AdEvent.ip_address == ip_address,
            models.AdEvent.created_at >= since,
        )
        .scalar()
        or 0
    )


def recent_click_events_for_device(db: Session, device_id: str) -> int:
    since = datetime.utcnow() - timedelta(hours=1)
    return int(
        db.query(func.count(models.AdEvent.id))
        .filter(
            models.AdEvent.event_type == models.EventType.click,
            models.AdEvent.device_id == device_id,
            models.AdEvent.created_at >= since,
        )
        .scalar()
        or 0
    )


def repeated_clicks_for_user_ad(db: Session, user_id: int, ad_id: int) -> int:
    since = datetime.utcnow() - timedelta(hours=1)
    return int(
        db.query(func.count(models.Click.id))
        .filter(
            models.Click.user_id == user_id,
            models.Click.ad_id == ad_id,
            models.Click.created_at >= since,
        )
        .scalar()
        or 0
    )


def fraud_alert_severity(risk_score: int) -> models.AlertSeverity:
    if risk_score >= INVALID_RISK_THRESHOLD:
        return models.AlertSeverity.high
    return models.AlertSeverity.medium
