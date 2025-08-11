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
    # Add url column to parent and default partition if they exist
    conn = op.get_bind()
    # Parent table
    op.add_column('article', sa.Column('url', sa.Text()), schema=None)
    # Best-effort: in native partitioning, adding to parent propagates to partitions
    # For safety, ensure default partition has the column
    try:
        conn.execute(sa.text('ALTER TABLE article_default ADD COLUMN IF NOT EXISTS url TEXT'))
    except Exception:
        pass


def downgrade() -> None:
    conn = op.get_bind()
    try:
        conn.execute(sa.text('ALTER TABLE article_default DROP COLUMN IF EXISTS url'))
    except Exception:
        pass
    op.drop_column('article', 'url', schema=None)


