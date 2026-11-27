"""Store a pending station identity separately from active enrollment."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"


def upgrade():
    op.add_column("palm_enrollments", sa.Column("pending_identity", sa.String(), nullable=True))


def downgrade():
    op.drop_column("palm_enrollments", "pending_identity")

