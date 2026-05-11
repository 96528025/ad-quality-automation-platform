"""fraud signals

Revision ID: 20260511_0004
Revises: 20260511_0003
Create Date: 2026-05-11
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260511_0004"
down_revision: str | None = "20260511_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ad_events", sa.Column("ip_address", sa.String(length=64), nullable=True))
    op.add_column("ad_events", sa.Column("device_id", sa.String(length=120), nullable=True))
    op.add_column("ad_events", sa.Column("user_agent", sa.String(length=255), nullable=True))
    op.add_column("ad_events", sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ad_events", sa.Column("is_invalid", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("ad_events", sa.Column("invalid_reason", sa.String(length=500), nullable=True))
    op.create_index("ix_ad_events_ip_address", "ad_events", ["ip_address"])
    op.create_index("ix_ad_events_device_id", "ad_events", ["device_id"])
    op.create_index("ix_ad_events_is_invalid", "ad_events", ["is_invalid"])


def downgrade() -> None:
    op.drop_index("ix_ad_events_is_invalid", table_name="ad_events")
    op.drop_index("ix_ad_events_device_id", table_name="ad_events")
    op.drop_index("ix_ad_events_ip_address", table_name="ad_events")
    op.drop_column("ad_events", "invalid_reason")
    op.drop_column("ad_events", "is_invalid")
    op.drop_column("ad_events", "risk_score")
    op.drop_column("ad_events", "user_agent")
    op.drop_column("ad_events", "device_id")
    op.drop_column("ad_events", "ip_address")
