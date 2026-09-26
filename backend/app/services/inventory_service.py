import uuid
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.facility import Facility
from app.models.inventory import InventoryItem
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryListResponse,
    InventorySummary,
)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, facility_id: uuid.UUID, data: InventoryItemCreate) -> InventoryItemResponse:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise AppException(status_code=404, detail="Facility not found")

        status_val = self._compute_status(data.quantity, data.reorder_threshold)

        item = InventoryItem(
            facility_id=facility_id,
            medication_id=data.medication_id,
            name=data.name,
            category=data.category,
            manufacturer=data.manufacturer,
            quantity=data.quantity,
            reorder_threshold=data.reorder_threshold,
            status=status_val,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return self._to_response(item)

    def list_inventory(
        self,
        facility_id: uuid.UUID,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> InventoryListResponse:
        stmt = select(InventoryItem).where(InventoryItem.facility_id == facility_id).order_by(desc(InventoryItem.updated_at))
        all_items = self.db.scalars(stmt).all()

        # Compute categories list
        categories = list(set(["All"] + [item.category for item in all_items]))

        # Compute summary metrics
        items_tracked = len(all_items)
        available_count = sum(1 for i in all_items if i.status == "Available")
        low_stock_count = sum(1 for i in all_items if i.status == "Low Stock")
        out_of_stock_count = sum(1 for i in all_items if i.status == "Unavailable")
        available_pct = Math_round((available_count / items_tracked) * 100) if items_tracked > 0 else 100

        reorder_alerts = [i.name for i in all_items if i.status in ["Low Stock", "Unavailable"]]

        summary = InventorySummary(
            items_tracked=items_tracked,
            available_percentage=available_pct,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            reorder_alerts=reorder_alerts,
        )

        # Filter items
        filtered = all_items
        if category and category != "All":
            filtered = [i for i in filtered if i.category.lower() == category.lower()]
        if query:
            q = query.lower()
            filtered = [i for i in filtered if q in i.name.lower()]

        items_resp = [self._to_response(i) for i in filtered]
        return InventoryListResponse(
            summary=summary,
            items=items_resp,
            categories=categories,
            total=len(items_resp),
        )

    def update_item(self, item_id: uuid.UUID, data: InventoryItemUpdate) -> InventoryItemResponse:
        item = self.db.get(InventoryItem, item_id)
        if not item:
            raise AppException(status_code=404, detail="Inventory item not found")

        if data.name is not None:
            item.name = data.name
        if data.category is not None:
            item.category = data.category
        if data.manufacturer is not None:
            item.manufacturer = data.manufacturer
        if data.quantity is not None:
            item.quantity = data.quantity
        if data.reorder_threshold is not None:
            item.reorder_threshold = data.reorder_threshold

        item.status = self._compute_status(item.quantity, item.reorder_threshold)
        self.db.commit()
        self.db.refresh(item)
        return self._to_response(item)

    def delete_item(self, item_id: uuid.UUID) -> dict:
        item = self.db.get(InventoryItem, item_id)
        if not item:
            raise AppException(status_code=404, detail="Inventory item not found")
        self.db.delete(item)
        self.db.commit()
        return {"status": "success", "message": "Inventory item deleted"}

    def _compute_status(self, qty: int, threshold: int) -> str:
        if qty <= 0:
            return "Unavailable"
        elif qty <= threshold:
            return "Low Stock"
        return "Available"

    def _to_response(self, item: InventoryItem) -> InventoryItemResponse:
        return InventoryItemResponse(
            id=item.id,
            facility_id=item.facility_id,
            facility_name=item.facility.name if item.facility else None,
            medication_id=item.medication_id,
            name=item.name,
            category=item.category,
            manufacturer=item.manufacturer,
            quantity=item.quantity,
            reorder_threshold=item.reorder_threshold,
            status=item.status,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


def Math_round(val: float) -> int:
    return int(round(val))
