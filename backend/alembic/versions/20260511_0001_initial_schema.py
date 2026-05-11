"""initial schema

Revision ID: 20260511_0001
Revises:
Create Date: 2026-05-11
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260511_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


campaign_status = sa.Enum("active", "paused", "ended", name="campaignstatus")
alert_severity = sa.Enum("low", "medium", "high", name="alertseverity")
alert_status = sa.Enum("open", "acknowledged", "investigating", "resolved", "false_positive", name="alertstatus")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("device", sa.String(length=32), nullable=False),
        sa.Column("interests", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_users_country", "users", ["country"])
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("advertiser_name", sa.String(length=120), nullable=False),
        sa.Column("daily_budget", sa.Float(), nullable=False),
        sa.Column("remaining_budget", sa.Float(), nullable=False),
        sa.Column("bid_cpc", sa.Float(), nullable=False),
        sa.Column("target_country", sa.String(length=2), nullable=False),
        sa.Column("target_age_min", sa.Integer(), nullable=False),
        sa.Column("target_age_max", sa.Integer(), nullable=False),
        sa.Column("status", campaign_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_campaigns_advertiser_name", "campaigns", ["advertiser_name"])
    op.create_index("ix_campaigns_id", "campaigns", ["id"])
    op.create_index("ix_campaigns_target_country", "campaigns", ["target_country"])

    op.create_table(
        "ads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("landing_url", sa.String(length=500), nullable=False),
        sa.Column("creative_url", sa.String(length=500), nullable=False),
    )
    op.create_index("ix_ads_campaign_id", "ads", ["campaign_id"])
    op.create_index("ix_ads_id", "ads", ["id"])

    op.create_table(
        "impressions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("ad_id", sa.Integer(), sa.ForeignKey("ads.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_impressions_ad_id", "impressions", ["ad_id"])
    op.create_index("ix_impressions_campaign_id", "impressions", ["campaign_id"])
    op.create_index("ix_impressions_created_at", "impressions", ["created_at"])
    op.create_index("ix_impressions_id", "impressions", ["id"])
    op.create_index("ix_impressions_user_id", "impressions", ["user_id"])

    op.create_table(
        "clicks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("impression_id", sa.Integer(), sa.ForeignKey("impressions.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("ad_id", sa.Integer(), sa.ForeignKey("ads.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_clicks_ad_id", "clicks", ["ad_id"])
    op.create_index("ix_clicks_campaign_id", "clicks", ["campaign_id"])
    op.create_index("ix_clicks_created_at", "clicks", ["created_at"])
    op.create_index("ix_clicks_id", "clicks", ["id"])
    op.create_index("ix_clicks_impression_id", "clicks", ["impression_id"])
    op.create_index("ix_clicks_user_id", "clicks", ["user_id"])

    op.create_table(
        "conversions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("click_id", sa.Integer(), sa.ForeignKey("clicks.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("conversion_value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("click_id", name="uq_conversion_click_id"),
    )
    op.create_index("ix_conversions_campaign_id", "conversions", ["campaign_id"])
    op.create_index("ix_conversions_click_id", "conversions", ["click_id"])
    op.create_index("ix_conversions_created_at", "conversions", ["created_at"])
    op.create_index("ix_conversions_id", "conversions", ["id"])
    op.create_index("ix_conversions_user_id", "conversions", ["user_id"])

    op.create_table(
        "quality_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("alert_type", sa.String(length=80), nullable=False),
        sa.Column("severity", alert_severity, nullable=False),
        sa.Column("status", alert_status, nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("owner", sa.String(length=120), nullable=True),
        sa.Column("resolution_note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_quality_alerts_alert_type", "quality_alerts", ["alert_type"])
    op.create_index("ix_quality_alerts_created_at", "quality_alerts", ["created_at"])
    op.create_index("ix_quality_alerts_id", "quality_alerts", ["id"])
    op.create_index("ix_quality_alerts_status", "quality_alerts", ["status"])

    op.create_table(
        "campaign_metrics_hourly",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("bucket_start", sa.DateTime(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("conversions", sa.Integer(), nullable=False),
        sa.Column("spend", sa.Float(), nullable=False),
        sa.Column("conversion_value", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("campaign_id", "bucket_start", name="uq_campaign_metrics_hourly_bucket"),
    )
    op.create_index("ix_campaign_metrics_hourly_bucket_start", "campaign_metrics_hourly", ["bucket_start"])
    op.create_index("ix_campaign_metrics_hourly_campaign_id", "campaign_metrics_hourly", ["campaign_id"])
    op.create_index("ix_campaign_metrics_hourly_id", "campaign_metrics_hourly", ["id"])


def downgrade() -> None:
    op.drop_table("campaign_metrics_hourly")
    op.drop_table("quality_alerts")
    op.drop_table("conversions")
    op.drop_table("clicks")
    op.drop_table("impressions")
    op.drop_table("ads")
    op.drop_table("campaigns")
    op.drop_table("users")
    alert_status.drop(op.get_bind(), checkfirst=True)
    alert_severity.drop(op.get_bind(), checkfirst=True)
    campaign_status.drop(op.get_bind(), checkfirst=True)

