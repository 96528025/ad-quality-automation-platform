from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.quality import run_quality_checks

router = APIRouter(prefix="/quality", tags=["quality"])


@router.post("/campaigns/{campaign_id}/run", response_model=list[schemas.QualityAlertRead])
def run_campaign_quality_checks(campaign_id: int, db: Session = Depends(get_db)):
    return run_quality_checks(db, campaign_id)


@router.get("/alerts", response_model=list[schemas.QualityAlertRead])
def list_alerts(db: Session = Depends(get_db)) -> list[models.QualityAlert]:
    return db.query(models.QualityAlert).order_by(models.QualityAlert.created_at.desc()).all()


@router.patch("/alerts/{alert_id}", response_model=schemas.QualityAlertRead)
def update_alert(
    alert_id: int,
    payload: schemas.QualityAlertUpdate,
    db: Session = Depends(get_db),
) -> models.QualityAlert:
    alert = db.get(models.QualityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert not found")

    alert.status = payload.status
    alert.owner = payload.owner
    alert.resolution_note = payload.resolution_note
    db.commit()
    db.refresh(alert)
    return alert
