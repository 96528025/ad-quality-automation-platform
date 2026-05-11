from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=schemas.CampaignRead, status_code=201)
def create_campaign(payload: schemas.CampaignCreate, db: Session = Depends(get_db)) -> models.Campaign:
    campaign = models.Campaign(**payload.model_dump(), remaining_budget=payload.daily_budget)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=list[schemas.CampaignRead])
def list_campaigns(db: Session = Depends(get_db)) -> list[models.Campaign]:
    return db.query(models.Campaign).order_by(models.Campaign.id).all()


@router.patch("/{campaign_id}/status", response_model=schemas.CampaignRead)
def update_campaign_status(
    campaign_id: int,
    payload: schemas.CampaignStatusUpdate,
    db: Session = Depends(get_db),
) -> models.Campaign:
    campaign = db.get(models.Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="campaign not found")
    campaign.status = payload.status
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/ads", response_model=schemas.AdRead, status_code=201)
def create_ad(campaign_id: int, payload: schemas.AdCreate, db: Session = Depends(get_db)) -> models.Ad:
    if campaign_id != payload.campaign_id:
        raise HTTPException(status_code=400, detail="campaign id mismatch")
    if db.get(models.Campaign, campaign_id) is None:
        raise HTTPException(status_code=404, detail="campaign not found")
    ad = models.Ad(**payload.model_dump(mode="json"))
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

