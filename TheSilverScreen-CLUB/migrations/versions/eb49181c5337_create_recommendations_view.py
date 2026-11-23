"""Create recommendations view

Revision ID: eb49181c5337
Revises: c7bf64a5b28e
Create Date: 2026-11-06 20:37:22.254009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb49181c5337'
down_revision = 'c7bf64a5b28e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE VIEW vw_recommendations AS
        SELECT
            r.id,
            r.sender_id,
            s.username AS sender_username,
            s.fullname AS sender_fullname,
            r.receiver_id,
            re.username AS receiver_username,
            re.fullname AS receiver_fullname,
            r.media_type,
            r.recommendation_id,
            r.created_at,
            r.title,
            r.poster_path,
            r.release_date,
            r.overview,
            r.popularity,
            r.vote_average,
            r.vote_count
        FROM recommendations AS r
        JOIN users AS s
            ON r.sender_id = s.user_id
        JOIN users AS re
            ON r.receiver_id = re.user_id
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS vw_recommendations")