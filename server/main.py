"""Main entrypoint for runner."""
import json 
import os
from typing import Optional

from bson import json_util
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pymongo.errors import PyMongoError

from server.common.db import get_collection
from server.common.logging import logger
from server.common.models import (
    AirBnbListingRequest, 
    AirBnbListingUpdate, 
    BatchEmbedRequest,
    SearchRequest
)
from server.search.generate_embeddings import embed_batch_of_documents
from server.search.search_index import create_search_index

# Load env variables. 
load_dotenv()


DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")


app = FastAPI()

# Connect to MongoDB client. 
try:
    collection = get_collection(DB_NAME, COLLECTION_NAME)
except RuntimeError as e:
    logger.error(f"Database access failed: {e}")
    raise HTTPException(
        status_code=500, 
        detail="Internal server error - DB access failed."
    )

    
    
@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """Search for Airbnb Listings."""
    try:
        doc = collection.find_one({"_id": doc_id})
        logger.info(f"Found document with ID: {doc_id}")
    except Exception as exc:
        logger.exception("MongoDB error on find_one")
        raise HTTPException(status_code=502, detail="Upstream database error") from exc
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return json.loads(json_util.dumps({"document": doc}))


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete document from collection."""
    logger.info(f"Request to delete document with ID: {doc_id}")
    try:
        doc = collection.find_one({"_id": doc_id})
        if not doc:
            logger.error(f"Document not found with ID: {doc_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        collection.delete_one({"_id": doc_id})
        return {"message": "Deleted", "id": doc_id}
    except PyMongoError as e:
        logger.exception(f"Database error during deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected server error")


@app.post("/documents")
def add_listing(request: AirBnbListingRequest):
    """Add a new listing."""
    try:
        doc = request.model_dump()
        # Check if document exists. 
        if doc.get("id"):
            existing = collection.find_one({"_id": doc["id"]})
            print(f"EXISTING: {existing}")
            if existing:
                raise HTTPException(status_code=400, detail="Document with this ID already exists")
            
        # Insert new listing. 
        doc["_id"] = doc.pop("id")
        
        # TODO: Add embedding of document
        result = collection.insert_one(doc)
        return {"message": "Listing added", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting new listing to Airbnb: {e}")
        raise HTTPException(status_code=500, detail=f"Error inserting document: {str(e)}")


@app.put("/documents/{doc_id}")
def update_document(doc_id: str, request: AirBnbListingUpdate):
    """Update an existing document in MongoDB."""
    existing_doc = collection.find_one({"_id": doc_id})
    if not existing_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Prepare update fields.
    update_data = {
        k: v for k, v in request.dict(exclude_unset=True).items()
        if v is not None
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    result = collection.update_one({"_id": doc_id}, {"$set": update_data})
    if result.modified_count == 0:
        return {"message": "No changes made", "id": doc_id}

    # Return updated document
    updated_doc = collection.find_one({"_id": doc_id})
    return json.loads(json_util.dumps({"document": updated_doc}))


@app.post("/documents/batch-embeddings")
def batch_embed_documents(
    query_batch_size: int = Query(50, ge=1),
    body: Optional[BatchEmbedRequest] = None
):
    """Embed a batch of documents from a collection. 
    
    Uses gemini embeddings to update each document with 
    embeddings field. 
    """
    batch_size = body.batch_size if body and body.batch_size else query_batch_size
    result = embed_batch_of_documents(
        collection, batch_size=batch_size)
    return result
    

@app.post("/search/create")
def batch_embed_documents():
    """Create a search index. 
    
    This is a one time activity for a colleciton. 
    """
    result = create_search_index(DB_NAME,  COLLECTION_NAME)
    return result

@app.post("/search")
def search_listings(request: SearchRequest):
    """Search for Airbnb listings."""
    print(request)
    return {"user_query": "user_query"}
