"""Powder repository for inventory operations."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..models import Powder
from .session import session_scope


class PowderRepository:
    def list_powders(
        self,
        *,
        query: str | None = None,
        manufacturer: str | None = None,
    ) -> Iterable[Powder]:
        stmt = select(Powder).order_by(Powder.powder_color)
        if query:
            like = f"%{query}%"
            stmt = stmt.filter(
                Powder.powder_color.ilike(like)
                | Powder.product_code.ilike(like)
                | Powder.color_family.ilike(like)
            )
        if manufacturer:
            stmt = stmt.filter(Powder.manufacturer == manufacturer)

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

    def list_color_families(self) -> list[str]:
        with session_scope() as session:
            rows = session.execute(
                select(Powder.color_family)
                .where(Powder.color_family.isnot(None))
                .distinct()
                .order_by(Powder.color_family)
            ).all()
            return [r[0] for r in rows if r and r[0]]

    def list_colors_full(self) -> list[dict]:
        with session_scope() as session:
            rows = session.execute(
                select(
                    Powder.powder_color.label("color"),
                    Powder.aliases.label("aliases"),
                    Powder.color_family.label("family"),
                ).order_by(Powder.powder_color)
            ).all()
            items: list[dict] = []
            for color, aliases, family in rows:
                items.append(
                    {
                        "color": color or "",
                        "aliases": aliases or "",
                        "family": family or "",
                    }
                )
            return items


powder_repo = PowderRepository()
