"""Utility Functions."""

import os
from typing import Any, List 

from dotenv import load_dotenv
from google import genai
from google.genai import types

from server.common.logging import logger

load_dotenv()

client = genai.Client(vertexai=False)


def gemini_embeddings_batch(texts: List[str]) -> List[Any]:
    """Embed a batch of texts."""
    try:
        # client = genai.Client(vertexai=False)
        result = client.models.embed_content(
            model=os.getenv("EMBEDDING_MODEL"),
            contents=texts,
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
        return result.embeddings
    except Exception as e:
        logger.error(f"Error embedding batch of docs! {e}")
        
    
    