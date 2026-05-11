from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.delivery import deliver_ad

router = APIRouter(prefix="/ads", tags=["ads"])


@router.post("/request", response_model=schemas.AdDeliveryRead)
def request_ad(payload: schemas.AdRequest, db: Session = Depends(get_db)) -> schemas.AdDeliveryRead:
    result = deliver_ad(db, payload.user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="no eligible ad found")

    ad, impression = result
    return schemas.AdDeliveryRead(
        campaign_id=ad.campaign_id,
        ad_id=ad.id,
        impression_id=impression.id,
        bid_cpc=ad.campaign.bid_cpc,
        landing_url=ad.landing_url,
    )

