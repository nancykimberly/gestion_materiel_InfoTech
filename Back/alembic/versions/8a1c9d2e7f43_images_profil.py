"""images profil et materiel

Revision ID: 8a1c9d2e7f43
Revises: 47d9d0e0f5c1
"""
from alembic import op
import sqlalchemy as sa

revision = "8a1c9d2e7f43"
down_revision = "47d9d0e0f5c1"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("utilisateurs", sa.Column("avatar_url", sa.Text(), nullable=True))
    op.add_column("materiels", sa.Column("image_url", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("materiels", "image_url")
    op.drop_column("utilisateurs", "avatar_url")
