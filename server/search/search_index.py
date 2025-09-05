"""Search an Index."""

import os
from typing import Any, Dict, List

from pymongo.operations import SearchIndexModel
from dotenv import load_dotenv
import voyageai

from server.common.db import client
from server.common.logging import logger
from server.common.utils import gemini_embed_documents
from server.search.generate_embeddings import cols_to_embed


load_dotenv()

vo = voyageai.Client()


def search_vector_store(
    user_query: str, 
    num_candidates: int, 
    limit: int,
    reviews_rating: int,
    return_full_documents: bool,
    similarity_threshold: float
):
    """Search Atlas Vector Search Index."""
    embedded_query = gemini_embed_documents(
            [user_query]
        )[0].values
    
    # Config with user query. 
    vector_search_config =  {
            '$vectorSearch': {
                'index': os.getenv("INDEX_NAME"), 
                'path': 'embedding', 
                'queryVector': embedded_query, 
                'numCandidates': num_candidates, 
                'limit': limit
            }
        }
        
    if reviews_rating:
        vector_search_config["$vectorSearch"]["filter"] = {
                '$and': [
                {
                    "review_scores.review_scores_value": {
                        "$gte": reviews_rating
                    }
                }
                ]
        }
    # Construct search pipeline. 
    pipeline = [vector_search_config]
    if return_full_documents:
        pipeline += [
            {
                "$addFields": {
                    "score": { "$meta": "vectorSearchScore" }
                }
            },
            {
                "$match": {
                    "score": { "$gte": similarity_threshold }
                }
            },
            {
                "$project": {
                    "embedding": 0  
                }
            }
        ]
    else:
        pipeline += [
            {
                "$project": {
                    "_id": 1, 
                    "review_scores.review_scores_value": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            },
            {
                "$match": {
                    "score": { "$gte": similarity_threshold }
                }
            },
        ]
        
    db_name = os.getenv("MONGO_DB_NAME")
    collection_name = os.getenv("MONGO_COLLECTION_NAME")
    # Get top results. 
    atlas_results = list(client[db_name][collection_name].aggregate(pipeline)) 
    return atlas_results


def rerank_results(
    atlas_results: List[Dict[str, Any]],
    user_query: str, 
    top_k: int
) -> List[Dict[str, Any]]:
    """Reranker of Vector Search results."""
    try:
        documents = []
        for res in atlas_results:
            curr_doc = ""
            for col in cols_to_embed:
                curr_doc += f"""
                {res.get(col, "")}
                """
            documents.append(curr_doc)
        
        reranking = vo.rerank(
            user_query, 
            documents, 
            model="rerank-2.5", 
            top_k=top_k
        )
        final_results = []
        for result in reranking.results:
            idx = result.index
            score = result.relevance_score
            doc = atlas_results[idx]
            doc_with_score = {**doc, "rerank_score": score}
            final_results.append(doc_with_score)  
        return final_results
    except Exception as e:
        logger.error(f"Error reranking results: {e}")


def get_search_results(
    user_query: str,
    num_candidates: int = 150, 
    limit: int = 10,
    top_k: int = 5, 
    return_full_documents: bool = True,
    similarity_threshold: float = 0.0,
    reviews_rating: int = None
) -> List[Dict[str, Any]]:
    # Embed user query. 
    try:
        # Semantic Search 
        atlas_results = search_vector_store(
            user_query=user_query,
            num_candidates=num_candidates,
            limit=limit,
            reviews_rating=reviews_rating,
            return_full_documents=return_full_documents,
            similarity_threshold=similarity_threshold
        )
        
        # Rerank retrieved documents. 
        final_results = rerank_results(atlas_results, user_query, top_k)
        
        # Quota error. 
        if not final_results:
            final_results = atlas_results
                     
        return {
            "num_results": len(final_results),
            "results": final_results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error searching index: {e}")
    
    
def create_search_index(
    database_name: str, 
    collection_name: str
) -> Dict[str, Any]:
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
                    },
                    {
                        "type": "filter",
                        "path": "review_scores.review_scores_value"
                    },
                ]
            },
            name="vector_index_filter",
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
