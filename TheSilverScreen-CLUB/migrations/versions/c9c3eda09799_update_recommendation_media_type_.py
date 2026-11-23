"""Update recommendation media type constraint

Revision ID: c9c3eda09799
Revises: 60b9c814c084
Create Date: 2026-11-05 16:25:41.918835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9c3eda09799'
down_revision = '60b9c814c084'
branch_labels = None
depends_on = None



def upgrade():
    op.drop_constraint(
        "chk_recommendation_media_type",
        "recommendations",
        type_="check"
    )

    op.create_check_constraint(
        "chk_recommendation_media_type",
        "recommendations",
        "media_type IN ('movie', 'tv')"
    )


def downgrade():
    op.drop_constraint(
        "chk_recommendation_media_type",
        "recommendations",
        type_="check"
    )

    op.create_check_constraint(
        "chk_recommendation_media_type",
        "recommendations",
        "media_type IN ('MOVIE', 'TV')"
    )