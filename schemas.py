"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Warehouse management schemas

class Item(BaseModel):
    """
    Items collection schema
    Collection: "item"
    """
    sku: str = Field(..., description="Stock Keeping Unit, unique identifier")
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    unit: str = Field("pcs", description="Unit of measure")
    min_stock: Optional[int] = Field(0, ge=0, description="Minimum desired stock level")

class Location(BaseModel):
    """
    Locations collection schema
    Collection: "location"
    """
    code: str = Field(..., description="Location code, e.g., A1-01")
    name: str = Field(..., description="Location name")
    type: str = Field("bin", description="Type of location: bin, rack, zone, etc.")

class Movement(BaseModel):
    """
    Inventory movements schema
    Collection: "movement"
    Quantity can be positive (inbound) or negative (outbound)
    """
    item_id: str = Field(..., description="Reference to Item _id as string")
    location_id: str = Field(..., description="Reference to Location _id as string")
    quantity: int = Field(..., description="Positive for IN, Negative for OUT")
    reference: Optional[str] = Field(None, description="Optional reference like PO/SO")
    note: Optional[str] = Field(None, description="Optional note")

# Example schemas kept for reference (not used by app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
