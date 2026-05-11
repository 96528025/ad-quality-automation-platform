"""raw event pipeline

Revision ID: 20260511_0003
Revises: 20260511_0002
Create Date: 2026-05-11
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260511_0003"
down_revision: str | None = "20260511_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

event_type = sa.Enum("impression", "click", "conversion", name="eventtype")
event_status = sa.Enum("pending", "processed", "failed", name="eventstatus")


def upgrade() -> None:
    bind = op.get_bind()
    event_type.create(bind, checkfirst=True)
    event_status.create(bind, checkfirst=True)

    op.create_table(
        "ad_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", event_type, nullable=False),
        sa.Column("status", event_status, nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("ad_id", sa.Integer(), sa.ForeignKey("ads.id"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("impression_id", sa.Integer(), sa.ForeignKey("impressions.id"), nullable=True),
        sa.Column("click_id", sa.Integer(), sa.ForeignKey("clicks.id"), nullable=True),
        sa.Column("conversion_value", sa.Float(), nullable=True),
        sa.Column("materialized_id", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("event_time", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_ad_events_id", "ad_events", ["id"])
    op.create_index("ix_ad_events_event_type", "ad_events", ["event_type"])
    op.create_index("ix_ad_events_status", "ad_events", ["status"])
    op.create_index("ix_ad_events_campaign_id", "ad_events", ["campaign_id"])
    op.create_index("ix_ad_events_ad_id", "ad_events", ["ad_id"])
    op.create_index("ix_ad_events_user_id", "ad_events", ["user_id"])
    op.create_index("ix_ad_events_impression_id", "ad_events", ["impression_id"])
    op.create_index("ix_ad_events_click_id", "ad_events", ["click_id"])
    op.create_index("ix_ad_events_event_time", "ad_events", ["event_time"])
    op.create_index("ix_ad_events_created_at", "ad_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("ad_events")
    event_status.drop(op.get_bind(), checkfirst=True)
    event_type.drop(op.get_bind(), checkfirst=True)
