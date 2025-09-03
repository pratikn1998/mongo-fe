
import certifi
import os 

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

from server.common.logging import logger
from server.common.utils import gemini_embeddings_batch

load_dotenv()

os.environ["GEMINI_API_KEY"] = "AIzaSyCXOed1u_Q61Vpu82aKigLJhJCSy2wRfbI"

logger.info("Connected to MongoDB successfully.")

result = gemini_embeddings_batch(["properties in Honolulu"])
embeddings = result[0].values 
# print(embeddings)
# 
# query_vector = 

# define pipeline
MONGO_CLIENT_URL = "mongodb+srv://edprajohjac_1:Focosquad1@cluster0.2cdptoa.mongodb.net/"
client = MongoClient(
    MONGO_CLIENT_URL,
    tls=True,
    tlsCAFile=certifi.where(), 
)
pipeline = [
  {
    '$vectorSearch': {
      'index': 'vector_index', 
      'path': 'embedding', 
      'queryVector': embeddings, 
      'numCandidates': 150, 
      'limit': 10
    }
  }, 
    {
    "$addFields": {
      "score": { "$meta": "vectorSearchScore" }
    }
  },
    {
    "$project": {
      "embedding": 0  # exclude the embedding field
    }
  }
]

# # run pipeline
result = client["sample_airbnb"]["listingsAndReviews"].aggregate(pipeline)

# print results
for i in result:
    # i["document"].pop("embedding")
    print(i)
    break