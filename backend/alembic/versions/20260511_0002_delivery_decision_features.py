"""delivery decision features

Revision ID: 20260511_0002
Revises: 20260511_0001
Create Date: 2026-05-11
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260511_0002"
down_revision: str | None = "20260511_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

review_status = sa.Enum("pending", "approved", "rejected", name="reviewstatus")


def upgrade() -> None:
    bind = op.get_bind()
    review_status.create(bind, checkfirst=True)

    op.add_column("campaigns", sa.Column("target_device", sa.String(length=32), nullable=False, server_default="any"))
    op.add_column("campaigns", sa.Column("target_interests", sa.String(length=255), nullable=False, server_default=""))
    op.add_column("campaigns", sa.Column("frequency_cap_per_day", sa.Integer(), nullable=False, server_default="10"))
    op.add_column("campaigns", sa.Column("pacing_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("ads", sa.Column("review_status", review_status, nullable=False, server_default="approved"))
    op.add_column("ads", sa.Column("predicted_ctr", sa.Float(), nullable=False, server_default="0.05"))
    op.add_column("ads", sa.Column("quality_score", sa.Float(), nullable=False, server_default="1.0"))
    op.create_index("ix_ads_review_status", "ads", ["review_status"])


def downgrade() -> None:
    op.drop_index("ix_ads_review_status", table_name="ads")
    op.drop_column("ads", "quality_score")
    op.drop_column("ads", "predicted_ctr")
    op.drop_column("ads", "review_status")

    op.drop_column("campaigns", "pacing_enabled")
    op.drop_column("campaigns", "frequency_cap_per_day")
    op.drop_column("campaigns", "target_interests")
    op.drop_column("campaigns", "target_device")

    review_status.drop(op.get_bind(), checkfirst=True)
