import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryListResponse,
)
from app.services.inventory_service import InventoryService

router = APIRouter(tags=["Facility Inventory"])


@router.post(
    "/facilities/{facility_id}/inventory",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an inventory item to a facility",
)
def create_inventory_item(
    facility_id: uuid.UUID,
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a medicine or medical supply item to a facility stock list."""
    service = InventoryService(db)
    return service.create_item(facility_id, payload)


@router.get(
    "/facilities/{facility_id}/inventory",
    response_model=InventoryListResponse,
    summary="Get facility inventory stock with metrics and alerts",
)
def get_facility_inventory(
    facility_id: uuid.UUID,
    category: Optional[str] = Query(None, description="Category filter e.g. Antibiotics, General"),
    query: Optional[str] = Query(None, description="Search query string"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve facility stock inventory list with stock metrics (items tracked, low stock, out of stock, reorder alerts)."""
    service = InventoryService(db)
    return service.list_inventory(facility_id, category=category, query=query)


@router.patch(
    "/inventory/{item_id}",
    response_model=InventoryItemResponse,
    summary="Update inventory item stock or details",
)
def update_inventory_item(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update stock quantity, threshold, or metadata for an inventory item."""
    service = InventoryService(db)
    return service.update_item(item_id, payload)


@router.delete(
    "/inventory/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an inventory item",
)
def delete_inventory_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an item from facility stock inventory."""
    service = InventoryService(db)
    service.delete_item(item_id)
