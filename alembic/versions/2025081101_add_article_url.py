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
    # Idempotent add with explicit existence checks for robustness
    conn = op.get_bind()

    # Add to parent table if missing
    exists_parent = conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'article' AND column_name = 'url'
            """
        )
    ).scalar()
    if not exists_parent:
        try:
            conn.execute(sa.text("ALTER TABLE article ADD COLUMN url TEXT"))
        except Exception:
            # Ignore if concurrently added or other non-fatal race
            pass

    # Add to default partition if it exists and column is missing
    try:
        has_partition = conn.execute(
            sa.text("SELECT to_regclass('public.article_default')")
        ).scalar()
        if has_partition:
            exists_part = conn.execute(
                sa.text(
                    """
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'article_default' AND column_name = 'url'
                    """
                )
            ).scalar()
            if not exists_part:
                conn.execute(sa.text("ALTER TABLE article_default ADD COLUMN url TEXT"))
    except Exception:
        # Ignore if partition lookup fails or permissions differ
        pass


def downgrade() -> None:
    # No-op: url existed in the base schema in some environments; avoid destructive downgrade
    pass


