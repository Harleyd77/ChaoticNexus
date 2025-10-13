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

    def get_powder(self, powder_id: int) -> Powder | None:
        with session_scope() as session:
            return session.get(Powder, powder_id)

    def find_by_color_name(self, color_name: str) -> Powder | None:
        with session_scope() as session:
            return (
                session.execute(select(Powder).filter(Powder.powder_color.ilike(color_name)))
                .scalars()
                .one_or_none()
            )

    def create_powder(self, **kwargs) -> Powder:
        with session_scope() as session:
            powder = Powder(**kwargs)
            session.add(powder)
            session.flush()
            return powder

    def update_powder(self, powder_id: int, **fields) -> Powder | None:
        with session_scope() as session:
            powder = session.get(Powder, powder_id)
            if not powder:
                return None
            for key, value in fields.items():
                if hasattr(powder, key):
                    setattr(powder, key, value)
            session.flush()
            return powder

    def delete_powder(self, powder_id: int) -> bool:
        with session_scope() as session:
            powder = session.get(Powder, powder_id)
            if not powder:
                return False
            session.delete(powder)
            session.flush()
            return True


powder_repo = PowderRepository()
