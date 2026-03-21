"""add_timescale_hypertables

Revision ID: 60c73cc76a81
Revises: 038807336256
Create Date: 2026-03-21 18:43:36.308365

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "60c73cc76a81"
down_revision: Union[str, Sequence[str], None] = "038807336256"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # Convert outbreak_data to hypertable
    op.execute(
        "SELECT create_hypertable('outbreak_data', 'date', if_not_exists => TRUE)"
    )

    # Convert environmental_data to hypertable
    op.execute(
        "SELECT create_hypertable('environmental_data', 'date', if_not_exists => TRUE)"
    )

    # Add compression settings
    op.execute(
        "ALTER TABLE outbreak_data SET (timescaledb.compress, "
        "timescaledb.compress_segmentby = 'region_id, disease_id')"
    )

    op.execute(
        "ALTER TABLE environmental_data SET (timescaledb.compress, "
        "timescaledb.compress_segmentby = 'region_id')"
    )

    # Add compression policy: compress data older than 30 days
    op.execute(
        "SELECT add_compression_policy('outbreak_data', "
        "INTERVAL '30 days', if_not_exists => TRUE)"
    )

    op.execute(
        "SELECT add_compression_policy('environmental_data', "
        "INTERVAL '30 days', if_not_exists => TRUE)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove compression policies
    op.execute("SELECT remove_compression_policy('outbreak_data', if_exists => TRUE)")
    op.execute(
        "SELECT remove_compression_policy('environmental_data', if_exists => TRUE)"
    )
