"""Service layer for powder inventory dashboards and actions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.models import InventoryLog, Powder, ReorderSetting
from app.repositories import inventory_repo


@dataclass
class InventorySummary:
    total_powders: int
    in_stock: int
    low_stock: int
    out_of_stock: int
    low_stock_threshold: float


class InventoryService:
    """Provide domain operations for inventory screens."""

    def __init__(self, repository=inventory_repo):
        self._repo = repository

    def powders_dashboard(
        self,
        *,
        search: str | None = None,
        manufacturer: str | None = None,
        low_stock_threshold: float = 5.0,
    ) -> tuple[list[Powder], InventorySummary]:
        powders = self._repo.list_powders_with_inventory(
            search=search,
            manufacturer=manufacturer,
        )

        in_stock_list: list[Powder] = []
        low_stock_list: list[Powder] = []
        out_of_stock_list: list[Powder] = []

        for powder in powders:
            stock_value = _coerce_float(powder.on_hand_kg or powder.in_stock)

            if stock_value <= 0:
                out_of_stock_list.append(powder)
            elif stock_value <= low_stock_threshold:
                low_stock_list.append(powder)
            else:
                in_stock_list.append(powder)

        summary = InventorySummary(
            total_powders=len(powders),
            in_stock=len(in_stock_list),
            low_stock=len(low_stock_list),
            out_of_stock=len(out_of_stock_list),
            low_stock_threshold=low_stock_threshold,
        )

        return powders, summary

    def recent_logs(self, powder_id: int, limit: int = 50) -> list[InventoryLog]:
        return self._repo.list_recent_inventory_logs(powder_id, limit=limit)

    def update_reorder_settings(
        self,
        powder_id: int,
        *,
        low_stock_threshold: float | None,
        reorder_quantity: float | None,
        supplier_info: str | None = None,
        notes: str | None = None,
    ) -> ReorderSetting:
        return self._repo.upsert_reorder_setting(
            powder_id,
            low_stock_threshold=low_stock_threshold,
            reorder_quantity=reorder_quantity,
            supplier_info=supplier_info,
            notes=notes,
        )

    def record_stock_update(
        self,
        powder_id: int,
        *,
        new_value: float,
        actor: str | None,
        notes: str | None,
    ) -> InventoryLog:
        powder = self._repo.get_powder(powder_id)
        old_value = getattr(powder, "on_hand_kg", None) if powder else None

        updated_powder = self._repo.update_powder_quantity(
            powder_id,
            on_hand_kg=new_value,
            last_weighed_kg=new_value,
        )

        log = self._repo.record_inventory_change(
            powder_id,
            change_type="manual_update",
            old_value=old_value,
            new_value=new_value,
            created_by=actor,
            notes=notes,
        )

        return log


def _coerce_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (float, int)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return 0.0


inventory_service = InventoryService()
