from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.services.metrics import campaign_metrics

CTR_ALERT_THRESHOLD = 0.30
CVR_ALERT_THRESHOLD = 0.50


def create_alert(
    db: Session,
    campaign_id: int,
    alert_type: str,
    severity: models.AlertSeverity,
    description: str,
) -> models.QualityAlert:
    alert = models.QualityAlert(
        campaign_id=campaign_id,
        alert_type=alert_type,
        severity=severity,
        description=description,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def run_quality_checks(db: Session, campaign_id: int) -> list[models.QualityAlert]:
    metrics = campaign_metrics(db, campaign_id)
    alerts: list[models.QualityAlert] = []

    if metrics["impressions"] and metrics["ctr"] > CTR_ALERT_THRESHOLD:
        alerts.append(
            create_alert(
                db,
                campaign_id,
                "high_ctr",
                models.AlertSeverity.high,
                f"CTR {metrics['ctr']:.2%} exceeds threshold {CTR_ALERT_THRESHOLD:.0%}.",
            )
        )

    if metrics["clicks"] and metrics["cvr"] > CVR_ALERT_THRESHOLD:
        alerts.append(
            create_alert(
                db,
                campaign_id,
                "high_cvr",
                models.AlertSeverity.medium,
                f"CVR {metrics['cvr']:.2%} exceeds threshold {CVR_ALERT_THRESHOLD:.0%}.",
            )
        )

    duplicate_clicks = (
        db.query(models.Click.user_id, models.Click.ad_id)
        .filter(models.Click.campaign_id == campaign_id)
        .group_by(models.Click.user_id, models.Click.ad_id)
        .having(func.count(models.Click.id) > 3)
        .all()
    )
    if duplicate_clicks:
        alerts.append(
            create_alert(
                db,
                campaign_id,
                "duplicate_click_pattern",
                models.AlertSeverity.medium,
                "Multiple repeated clicks from the same user and ad were detected.",
            )
        )

    return alerts
