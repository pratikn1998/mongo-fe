"""Generate Emebddings using gemini."""

from typing import Any, Dict 

from pymongo import UpdateOne
from tqdm import tqdm

from server.common.logging import logger
from server.common.utils import gemini_embed_documents


cols_to_embed = [
    "name",
    "summary",
    "property_type",
    "amenities",
    "cancellation_policy",
    "address",
]


def build_text(doc: Dict[str, Any]) -> str:
    """Build text to embed.
    
    Args:
        doc: Airbnb listing / document.  
    """
    text = ""
    for col in cols_to_embed:
        text += f"""
        {col}: {doc.get(col, "")}
        """
    return text.strip()
    

# NOTE: The function below can be used as a pub/sub function -> 
# Listening to a queue of documentst that get inserted to the 
# collection. 
def embed_batch_of_documents(collection, batch_size):
    """Embed a batch of documents."""

    # NOTE: Would have used asyncio gather instead but due to Gemini Embeddings quota
    # used while loop. 
    total_to_embed = collection.count_documents({"embedding": {"$exists": False}})
    logger.info(f"Documents without embedding: {total_to_embed}")
    
    documents_embedded = 0
    
    with tqdm(total=total_to_embed, desc="Embedding documents", unit="doc") as pbar:
        while True:
            docs = list(collection.find({"embedding": {"$exists": False}}).limit(batch_size))
            if not docs:
                logger.info("No more documents to embed.")
                break
            inputs = [build_text(doc) for doc in docs]
            embeddings = gemini_embed_documents(inputs)
            
            # Store batch updates. 
            updates = []
            if embeddings:
                for doc, embedding in zip(docs, embeddings):
                    updates.append(
                        UpdateOne(
                            {"_id": doc["_id"]},
                            {"$set": {"embedding": embedding.values}}
                        )
                    )
            if updates: 
                result = collection.bulk_write(updates, ordered=False)
                modified_count = result.modified_count
                documents_embedded += modified_count
                logger.info(f"Updated {modified_count} documents with embeddings")
                pbar.update(modified_count)

        
    count = collection.count_documents({"embedding": {"$exists": True}})
    logger.info(f"Documents with embedding: {count}")
    return {
        "documents_to_embed": total_to_embed,
        "documents_embedded": documents_embedded,
        "msg": f"Documents updated with embeddings: {count}"
    }
