from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.metrics import campaign_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/campaigns/{campaign_id}", response_model=schemas.CampaignMetrics)
def get_campaign_metrics(campaign_id: int, db: Session = Depends(get_db)):
    try:
        return campaign_metrics(db, campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

