"""Inventory repository for powder stock management."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import InventoryLog, Powder, ReorderSetting
from .session import session_scope


class InventoryRepository:
    """Encapsulates data access for powder inventory features."""

    def list_powders_with_inventory(
        self,
        *,
        search: str | None = None,
        manufacturer: str | None = None,
    ) -> list[Powder]:
        """Return powders with related inventory metadata eagerly loaded."""

        stmt = (
            select(Powder)
            .options(
                selectinload(Powder.reorder_settings),
                selectinload(Powder.inventory_logs),
            )
            .order_by(Powder.powder_color)
        )

        if search:
            like = f"%{search}%"
            stmt = stmt.filter(
                Powder.powder_color.ilike(like)
                | Powder.product_code.ilike(like)
                | Powder.manufacturer.ilike(like)
                | Powder.color_family.ilike(like)
            )

        if manufacturer:
            stmt = stmt.filter(Powder.manufacturer == manufacturer)

        with session_scope() as session:
            return session.execute(stmt).scalars().unique().all()

    def get_powder(self, powder_id: int) -> Powder | None:
        """Fetch a single powder by identifier."""

        with session_scope() as session:
            return session.get(Powder, powder_id)

    def list_recent_inventory_logs(self, powder_id: int, limit: int = 50) -> list[InventoryLog]:
        """Return the most recent inventory log entries for a powder."""

        stmt = (
            select(InventoryLog)
            .filter(InventoryLog.powder_id == powder_id)
            .order_by(InventoryLog.created_at.desc())
            .limit(limit)
        )

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

    def upsert_reorder_setting(
        self,
        powder_id: int,
        *,
        low_stock_threshold,
        reorder_quantity,
        supplier_info: str | None = None,
        notes: str | None = None,
    ) -> ReorderSetting:
        """Create or update reorder settings for a powder."""

        with session_scope() as session:
            setting = (
                session.query(ReorderSetting)
                .filter(ReorderSetting.powder_id == powder_id)
                .one_or_none()
            )

            if setting is None:
                setting = ReorderSetting(powder_id=powder_id)
                session.add(setting)

            setting.low_stock_threshold = low_stock_threshold
            setting.reorder_quantity = reorder_quantity
            setting.supplier_info = supplier_info
            setting.notes = notes

            session.flush()
            return setting

    def record_inventory_change(
        self,
        powder_id: int,
        *,
        change_type: str,
        old_value,
        new_value,
        created_by: str | None = None,
        notes: str | None = None,
    ) -> InventoryLog:
        """Persist an inventory log entry."""

        with session_scope() as session:
            log = InventoryLog(
                powder_id=powder_id,
                change_type=change_type,
                old_value=old_value,
                new_value=new_value,
                created_by=created_by,
                notes=notes,
            )
            session.add(log)
            session.flush()
            return log

    def update_powder_quantity(
        self,
        powder_id: int,
        *,
        on_hand_kg,
        last_weighed_kg,
    ) -> Powder | None:
        """Update powder inventory quantities and return the updated powder."""

        with session_scope() as session:
            powder = session.get(Powder, powder_id)
            if powder is None:
                return None

            if on_hand_kg is not None:
                powder.on_hand_kg = on_hand_kg
            if last_weighed_kg is not None:
                powder.last_weighed_kg = last_weighed_kg

            session.flush()
            return powder


inventory_repo = InventoryRepository()

__all__: Sequence[str] = ["InventoryRepository", "inventory_repo"]
