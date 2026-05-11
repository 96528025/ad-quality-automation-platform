from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.attribution import record_click, record_conversion

router = APIRouter(prefix="/events", tags=["events"])


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

