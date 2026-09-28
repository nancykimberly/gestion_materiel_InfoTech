"""ajout activation compte

Revision ID: 47d9d0e0f5c1
Revises: 1e28afcc55e3
"""

from alembic import op
import sqlalchemy as sa

revision = "47d9d0e0f5c1"
down_revision = "1e28afcc55e3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("utilisateurs", sa.Column("doit_changer_mot_de_passe", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column("utilisateurs", "doit_changer_mot_de_passe")
