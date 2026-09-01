"""Add data origin to event records.

Revision ID: 494432d1d9c5
Revises: 820e9d52f121
Create Date: 2026-08-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "494432d1d9c5"
down_revision: Union[str, Sequence[str], None] = "820e9d52f121"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    origin = sa.Column("data_origin", sa.String(length=16), nullable=False, server_default="LIVE")
    op.add_column("security_events", origin.copy())
    op.add_column("plate_events", origin.copy())
    op.create_index("ix_security_events_data_origin", "security_events", ["data_origin"])
    op.create_index("ix_plate_events_data_origin", "plate_events", ["data_origin"])

    # Preserve already-labelled seeded records when upgrading an existing demo database.
    op.execute(
        "UPDATE security_events SET data_origin = 'DEMO' "
        "WHERE track_id LIKE 'DEMO-%' OR operator_notes LIKE '%SIMULATED%'"
    )
    op.execute("UPDATE plate_events SET data_origin = 'DEMO' WHERE track_id LIKE 'DEMO-%'")


def downgrade() -> None:
    op.drop_index("ix_plate_events_data_origin", table_name="plate_events")
    op.drop_index("ix_security_events_data_origin", table_name="security_events")
    op.drop_column("plate_events", "data_origin")
    op.drop_column("security_events", "data_origin")
