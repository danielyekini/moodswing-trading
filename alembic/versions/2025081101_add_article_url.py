"""add article.url column

Revision ID: 2025081101
Revises: 48dc301d6e3d
Create Date: 2025-08-11

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025081101'
down_revision = '48dc301d6e3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent add: only add if the column does not yet exist
    conn = op.get_bind()
    conn.execute(sa.text('ALTER TABLE article ADD COLUMN IF NOT EXISTS url TEXT'))
    # Ensure default partition also has the column (if using a default partition)
    try:
        conn.execute(sa.text('ALTER TABLE article_default ADD COLUMN IF NOT EXISTS url TEXT'))
    except Exception:
        # In environments without a default partition, ignore
        pass


def downgrade() -> None:
    # No-op: url existed in the base schema in some environments; avoid destructive downgrade
    pass


