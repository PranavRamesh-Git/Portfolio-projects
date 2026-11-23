"""Update movies and TV library schema

Revision ID: 5bede8c4a40d
Revises: e7acf2289dba
Create Date: 2026-10-26 12:36:00.196045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bede8c4a40d'
down_revision = 'e7acf2289dba'
branch_labels = None
depends_on = None



def upgrade():

    # ================================
    # 1. MODIFY tblmovies
    # ================================

    # Rename the existing column.
    # This preserves its True/False values.
    op.alter_column(
        "tblmovies",
        "watchlist_status",
        new_column_name="library_status"
    )

    # Remove the two unwanted columns.
    op.drop_column("tblmovies", "favourites")
    op.drop_column("tblmovies", "rewatch")

    # Remove the old CHECK constraint.
    op.drop_constraint(
        "ck_movie_status",
        "tblmovies",
        type_="check"
    )

    # Add the updated CHECK constraint.
    op.create_check_constraint(
        "ck_movie_status",
        "tblmovies",
        "status IN ("
        "'CURRENTLY WATCHING', "
        "'DROPPED', "
        "'FINISHED', "
        "'WATCHLIST', "
        "'NEXT WATCH', "
        "'FAVORITE'"
        ")"
    )

    # ================================
    # 2. MODIFY tbltv
    # ================================

    op.alter_column(
        "tbltv",
        "watchlist_status",
        new_column_name="library_status"
    )

    op.drop_column("tbltv", "favourites")
    op.drop_column("tbltv", "rewatch")

    op.drop_constraint(
        "ck_tv_status",
        "tbltv",
        type_="check"
    )

    op.create_check_constraint(
        "ck_tv_status",
        "tbltv",
        "status IN ("
        "'CURRENTLY WATCHING', "
        "'DROPPED', "
        "'FINISHED', "
        "'WATCHLIST', "
        "'NEXT WATCH', "
        "'FAVORITE'"
        ")"
    )


def downgrade():

    # ================================
    # 1. RESTORE tbltv
    # ================================

    # Remove the new constraint.
    op.drop_constraint(
        "ck_tv_status",
        "tbltv",
        type_="check"
    )

    # Restore the original constraint.
    op.create_check_constraint(
        "ck_tv_status",
        "tbltv",
        "status IN ("
        "'CURRENTLY WATCHING', "
        "'DROPPED', "
        "'FINISHED'"
        ")"
    )

    # Rename library_status back.
    op.alter_column(
        "tbltv",
        "library_status",
        new_column_name="watchlist_status"
    )

    # Recreate removed columns.
    op.add_column(
        "tbltv",
        sa.Column(
            "favourites",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.add_column(
        "tbltv",
        sa.Column(
            "rewatch",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    # ================================
    # 2. RESTORE tblmovies
    # ================================

    op.drop_constraint(
        "ck_movie_status",
        "tblmovies",
        type_="check"
    )

    op.create_check_constraint(
        "ck_movie_status",
        "tblmovies",
        "status IN ("
        "'CURRENTLY WATCHING', "
        "'DROPPED', "
        "'FINISHED'"
        ")"
    )

    op.alter_column(
        "tblmovies",
        "library_status",
        new_column_name="watchlist_status"
    )

    op.add_column(
        "tblmovies",
        sa.Column(
            "favourites",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.add_column(
        "tblmovies",
        sa.Column(
            "rewatch",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )
