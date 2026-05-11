from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.attribution import record_click, record_conversion
from app.services.event_pipeline import ingest_event, process_pending_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{event_id}", response_model=schemas.AdEventRead)
def get_ad_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.AdEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return event


@router.post("/click", response_model=schemas.ClickRead, status_code=201)
def create_click(payload: schemas.ClickCreate, db: Session = Depends(get_db)):
    try:
        return record_click(db, payload.impression_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/conversion", response_model=schemas.ConversionRead, status_code=201)
def create_conversion(payload: schemas.ConversionCreate, db: Session = Depends(get_db)):
    try:
        return record_conversion(db, payload.click_id, payload.conversion_value, payload.created_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ingest", response_model=schemas.AdEventRead, status_code=202)
def ingest_ad_event(payload: schemas.AdEventCreate, db: Session = Depends(get_db)):
    return ingest_event(
        db,
        event_type=payload.event_type,
        campaign_id=payload.campaign_id,
        ad_id=payload.ad_id,
        user_id=payload.user_id,
        impression_id=payload.impression_id,
        click_id=payload.click_id,
        conversion_value=payload.conversion_value,
        event_time=payload.event_time,
    )


@router.post("/process-pending", response_model=schemas.EventProcessResult)
def process_pending_ad_events(limit: int = 100, db: Session = Depends(get_db)):
    processed, failed = process_pending_events(db, limit=limit)
    return schemas.EventProcessResult(processed=processed, failed=failed)
