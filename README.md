# MongoDB FE Coding Interview

A FastAPI-based semantic search application for Airbnb listings using MongoDB Atlas Vector Search. This application provides intelligent search capabilities over Airbnb property data with vector embeddings and reranking.

## 🚀 Features

- **Semantic Search**: Vector-based search using MongoDB Atlas Vector Search
- **Document Management**: Full CRUD operations for Airbnb listings
- **Batch Embeddings**: Generate embeddings for documents using Google Gemini
- **Reranking**: Advanced result reranking using Voyage AI
- **Filtering**: Search with rating filters and similarity thresholds
- **RESTful API**: Clean FastAPI endpoints with automatic documentation

## 🏗️ Architecture

- **Backend**: FastAPI with Python 3.11+
- **Database**: MongoDB Atlas with Vector Search
- **Embeddings**: Google Gemini API for text embeddings
- **Reranking**: Voyage AI for result optimization
- **Data Models**: Pydantic models with MongoDB-specific field types

## 📋 Prerequisites

- Python 3.11+
- MongoDB Atlas cluster with Vector Search enabled
- Google Gemini API key
- Voyage AI API key

## 🛠️ Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# MongoDB Configuration
MONGO_DB_NAME=your_database_name
MONGO_COLLECTION_NAME=your_collection_name
MONGO_URI=your_mongodb_atlas_connection_string

# API Keys
GOOGLE_API_KEY=your_google_gemini_api_key
VOYAGE_API_KEY=your_voyage_ai_api_key
```

### 3. Database Setup

1. Ensure your MongoDB Atlas cluster has Vector Search enabled
2. Create the vector search index by calling the `/search/create` endpoint after starting the server

## 🚀 Running the Application

### Development Server

```bash
uvicorn server.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/documents/{doc_id}` | Retrieve a specific document |
| `POST` | `/documents` | Create a new Airbnb listing |
| `PUT` | `/documents/{doc_id}` | Update an existing listing |
| `DELETE` | `/documents/{doc_id}` | Delete a document |

### Search & Embeddings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search` | Semantic search with vector embeddings |
| `POST` | `/search/create` | Create vector search index |
| `POST` | `/documents/batch-embeddings` | Generate embeddings for documents |

## 🔍 Search API Usage

### Basic Search Request

```json
{
  "user_query": "airbnbs in warm and sunny places with a pool",
  "num_candidates": 150,
  "limit": 10,
  "top_k": 5,
  "return_full_documents": true,
  "similarity_threshold": 0.6,
  "reviews_rating": 4
}
```

### Search Parameters

- `user_query` (required): Natural language search query
- `num_candidates`: Number of candidates to retrieve from vector search (default: 150)
- `limit`: Maximum results to return (default: 10)
- `top_k`: Number of top results after reranking (default: 5)
- `return_full_documents`: Whether to return complete documents or just IDs (default: true)
- `similarity_threshold`: Minimum similarity score (default: 0.6)
- `reviews_rating`: Filter by minimum review rating (optional)

## 📊 Data Models

### Airbnb Listing Structure

The application handles comprehensive Airbnb listing data including:

- **Basic Info**: Name, description, property type, room type
- **Location**: Address, neighborhood overview, transit information
- **Pricing**: Price, weekly/monthly rates, cleaning fees
- **Amenities**: Property amenities and features
- **Reviews**: Review scores and ratings
- **Availability**: Calendar and booking information


## 🔧 Development

### Project Structure

```
├── server/
│   ├── common/           # Shared utilities and models
│   │   ├── db.py        # Database connection
│   │   ├── models.py    # Pydantic data models
│   │   ├── utils.py     # Utility functions
│   │   └── logging.py   # Logging configuration
│   ├── search/          # Search functionality
│   │   ├── search_index.py      # Vector search operations
│   │   └── generate_embeddings.py # Embedding generation
│   └── main.py          # FastAPI application
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

