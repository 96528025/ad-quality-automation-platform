from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CampaignStatus(str, Enum):
    active = "active"
    paused = "paused"
    ended = "ended"


class AlertSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AlertStatus(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country: Mapped[str] = mapped_column(String(2), index=True)
    age: Mapped[int] = mapped_column(Integer)
    device: Mapped[str] = mapped_column(String(32))
    interests: Mapped[str] = mapped_column(String(255), default="")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    advertiser_name: Mapped[str] = mapped_column(String(120), index=True)
    daily_budget: Mapped[float] = mapped_column(Float)
    remaining_budget: Mapped[float] = mapped_column(Float)
    bid_cpc: Mapped[float] = mapped_column(Float)
    target_country: Mapped[str] = mapped_column(String(2), index=True)
    target_age_min: Mapped[int] = mapped_column(Integer)
    target_age_max: Mapped[int] = mapped_column(Integer)
    status: Mapped[CampaignStatus] = mapped_column(SqlEnum(CampaignStatus), default=CampaignStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ads: Mapped[list["Ad"]] = relationship(back_populates="campaign")


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    landing_url: Mapped[str] = mapped_column(String(500))
    creative_url: Mapped[str] = mapped_column(String(500), default="")

    campaign: Mapped[Campaign] = relationship(back_populates="ads")


class Impression(Base):
    __tablename__ = "impressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    impression_id: Mapped[int] = mapped_column(ForeignKey("impressions.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Conversion(Base):
    __tablename__ = "conversions"
    __table_args__ = (UniqueConstraint("click_id", name="uq_conversion_click_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    click_id: Mapped[int] = mapped_column(ForeignKey("clicks.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    conversion_value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class QualityAlert(Base):
    __tablename__ = "quality_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[AlertSeverity] = mapped_column(SqlEnum(AlertSeverity), default=AlertSeverity.medium)
    status: Mapped[AlertStatus] = mapped_column(SqlEnum(AlertStatus), default=AlertStatus.open, index=True)
    description: Mapped[str] = mapped_column(String(500))
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CampaignMetricsHourly(Base):
    __tablename__ = "campaign_metrics_hourly"
    __table_args__ = (UniqueConstraint("campaign_id", "bucket_start", name="uq_campaign_metrics_hourly_bucket"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    bucket_start: Mapped[datetime] = mapped_column(DateTime, index=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_value: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
