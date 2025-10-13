"""add ticker_universe table

Revision ID: 2025090701
Revises: 2025081101
Create Date: 2025-09-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025090701'
down_revision = '2025081101'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name

    # Create table in a portable way across Postgres and SQLite
    op.create_table(
        'ticker_universe',
        sa.Column('ticker', sa.Text(), primary_key=True, nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE') if dialect == 'postgresql' else sa.text('1')),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Basic index to support listing active tickers quickly
    op.create_index('ticker_universe_active_idx', 'ticker_universe', ['active'])


def downgrade() -> None:
    op.drop_index('ticker_universe_active_idx', table_name='ticker_universe')
    op.drop_table('ticker_universe')


