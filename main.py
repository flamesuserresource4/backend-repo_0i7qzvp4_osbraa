import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Item, Location, Movement

app = FastAPI(title="Warehouse Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_str_id(doc):
    if not doc:
        return doc
    d = doc.copy()
    if d.get("_id"):
        d["_id"] = str(d["_id"])
    return d

# Routes

@app.get("/")
def read_root():
    return {"message": "Warehouse Management Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Items
@app.post("/api/items", response_model=dict)
def create_item(item: Item):
    try:
        inserted_id = create_document("item", item)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/items", response_model=List[dict])
def list_items(q: Optional[str] = None, limit: int = 50):
    filt = {}
    if q:
        # Simple name filter
        filt = {"name": {"$regex": q, "$options": "i"}}
    try:
        docs = get_documents("item", filt, limit)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Locations
@app.post("/api/locations", response_model=dict)
def create_location(location: Location):
    try:
        inserted_id = create_document("location", location)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/locations", response_model=List[dict])
def list_locations(q: Optional[str] = None, limit: int = 50):
    filt = {}
    if q:
        filt = {"name": {"$regex": q, "$options": "i"}}
    try:
        docs = get_documents("location", filt, limit)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Movements
@app.post("/api/movements", response_model=dict)
def create_movement(movement: Movement):
    try:
        inserted_id = create_document("movement", movement)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock", response_model=List[dict])
def current_stock(limit: int = 100):
    """
    Compute stock by aggregating movements.
    Note: using simple Python aggregation for demo; for large data, use MongoDB aggregation.
    """
    try:
        items = {str(d["_id"]): d for d in get_documents("item", {}, None)}
        movements = get_documents("movement", {}, None)
        stock = {}
        for mv in movements:
            item_id = str(mv.get("item_id"))
            qty = int(mv.get("quantity", 0))
            stock[item_id] = stock.get(item_id, 0) + qty
        # Build response
        res = []
        for item_id, qty in stock.items():
            item = items.get(item_id)
            if item:
                res.append({
                    "item_id": item_id,
                    "sku": item.get("sku"),
                    "name": item.get("name"),
                    "quantity": qty
                })
        return sorted(res, key=lambda x: x["name"])[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
