"""constraints

Revision ID: 95985e696916
Revises: 55d34cf79984
Create Date: 2026-01-24 15:38:18.438719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from backend.src.films.domain.entities.constants import MovieType, Genre, Profession

# revision identifiers, used by Alembic.
revision: str = '95985e696916'
down_revision: Union[str, Sequence[str], None] = '55d34cf79984'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

types = [{"id": int(mt), "name": str(mt)} for mt in MovieType]
genres = [{"name": str(genre)} for genre in Genre]
professions = [{"name": str(profession)} for profession in Profession]


def upgrade() -> None:
    """Upgrade schema."""
    op.bulk_insert(
        table=sa.table(
            "types",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
        ),
        rows=types,
    )

    op.bulk_insert(
        table=sa.table("genres", sa.column("name", sa.String)),
        rows=genres,
    )

    op.bulk_insert(
        table=sa.table("professions", sa.column("name", sa.String)),
        rows=professions,
    )


def downgrade() -> None:
    """Downgrade schema."""

    type_ids = tuple(t["id"] for t in types)
    genre_names = tuple(g["name"] for g in genres)
    profession_names = tuple(p["name"] for p in professions)

    op.execute("DELETE FROM movie_country")
    op.execute("DELETE FROM movie_genre")
    op.execute("DELETE FROM person_movie")

    op.execute("DELETE FROM movies")

    op.execute("DELETE FROM related_groups")

    op.execute("DELETE FROM persons")

    op.execute(f"DELETE FROM professions WHERE name IN {profession_names}")
    op.execute(f"DELETE FROM genres WHERE name IN {genre_names}")
    op.execute(f"DELETE FROM types WHERE id IN {type_ids}")