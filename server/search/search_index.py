"""Search an Index."""

from pymongo.operations import SearchIndexModel

from server.common.db import client
from server.common.logging import logger


def create_search_index(database_name: str, collection_name: str):
    try:
        db = client[database_name]
        collection = db[collection_name]
        search_index_model = SearchIndexModel(
        definition={
            "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 768,
                "similarity": "cosine"
            }
            ]
        },
        name="vector_index",
        type="vectorSearch",
        )

        # Create the index.
        result = collection.create_search_index(model=search_index_model)
        logger.info("MongoDB Vector Search Index Created")
        return {
            "index_name": result,
            "status": "created"
        }
    except Exception as e:
        logger.info("Unexpected error creating search index.")
        raise RuntimeError("Unexpected error creating search index") from e