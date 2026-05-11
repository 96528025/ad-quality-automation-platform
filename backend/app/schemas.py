from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models import AlertSeverity, AlertStatus, CampaignStatus


class UserCreate(BaseModel):
    country: str = Field(min_length=2, max_length=2)
    age: int = Field(ge=0, le=120)
    device: str
    interests: str = ""


class UserRead(UserCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CampaignCreate(BaseModel):
    advertiser_name: str
    daily_budget: float = Field(gt=0)
    bid_cpc: float = Field(gt=0)
    target_country: str = Field(min_length=2, max_length=2)
    target_age_min: int = Field(ge=0, le=120)
    target_age_max: int = Field(ge=0, le=120)
    status: CampaignStatus = CampaignStatus.active

    @model_validator(mode="after")
    def validate_age_range(self) -> "CampaignCreate":
        if self.target_age_min > self.target_age_max:
            raise ValueError("target_age_min must be <= target_age_max")
        return self


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    advertiser_name: str
    daily_budget: float
    remaining_budget: float
    bid_cpc: float
    target_country: str
    target_age_min: int
    target_age_max: int
    status: CampaignStatus


class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus


class AdCreate(BaseModel):
    campaign_id: int
    title: str
    landing_url: HttpUrl
    creative_url: str = ""


class AdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    title: str
    landing_url: str
    creative_url: str


class AdRequest(BaseModel):
    user_id: int


class AdDeliveryRead(BaseModel):
    campaign_id: int
    ad_id: int
    impression_id: int
    bid_cpc: float
    landing_url: str


class ClickCreate(BaseModel):
    impression_id: int


class ClickRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    impression_id: int
    campaign_id: int
    ad_id: int
    user_id: int


class ConversionCreate(BaseModel):
    click_id: int
    conversion_value: float = Field(gt=0)
    created_at: datetime | None = None


class ConversionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    click_id: int
    campaign_id: int
    user_id: int
    conversion_value: float


class CampaignMetrics(BaseModel):
    campaign_id: int
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    cvr: float
    spend: float
    remaining_budget: float


class QualityAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    alert_type: str
    severity: AlertSeverity
    status: AlertStatus
    description: str
    owner: str | None = None
    resolution_note: str | None = None
    created_at: datetime
    updated_at: datetime


class QualityAlertUpdate(BaseModel):
    status: AlertStatus
    owner: str | None = Field(default=None, max_length=120)
    resolution_note: str | None = Field(default=None, max_length=500)
