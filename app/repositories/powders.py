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


powder_repo = PowderRepository()
