# 📰 Modern News Aggregator API

A production-ready, high-performance news aggregator built with **FastAPI**, **PostgreSQL**, and **Celery**. This system automatically fetches, deduplicates, and serves news articles from multiple global sources.

---

## 🚀 Features

- **Async Core**: Leveraging `FastAPI` and `SQLAlchemy 2.0` with `asyncpg` for non-blocking I/O.
- **Multi-Source Integration**: 
  - [NewsAPI.org](https://newsapi.org/)
  - [The Guardian](https://open-platform.theguardian.com/)
  - [New York Times](https://developer.nytimes.com/)
- **Background Tasks**: Scheduled ingestion using `Celery` and `Redis`.
- **Intelligent Deduplication**: Uses SHA256 URL hashing to ensure no duplicate articles are stored.
- **High-Performance Search**: PostgreSQL `GIN` indexes and `pg_trgm` for fast full-text search across titles and descriptions.
- **Caching Layer**: Redis-based caching for API endpoints to ensure sub-millisecond response times.
- **Robust Schema**: Timezone-aware metadata, JSONB storage for raw data, and optimized indexing.

---

## 🛠 Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Cache**: Redis
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Deployment**: Docker & Docker Compose

---

## ⚙️ Getting Started

### 1. Clone & Environment
Rename `.env.example` to `.env` and fill in your API keys:
```bash
# PostgreSQL
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/newsaggregator"
# Redis
REDIS_URL="redis://localhost:6379/0"
# APIs
NEWSAPI_KEY="your_key"
GUARDIAN_API_KEY="your_key"
NYTIMES_API_KEY="your_key"
```

### 2. Run with Docker (Recommended)
This starts the API, PostgreSQL, Redis, and Celery workers in one command:
```bash
docker-compose up --build
```

### 3. Run Locally (Windows)
If you have PostgreSQL and Redis (via WSL/Native) running:
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Services**:
   Double-click `run_local.bat` or run it from the terminal:
   ```bash
   .\run_local.bat
   ```

---

## 📖 API Documentation

Once the app is running, access the interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints
- `GET /api/v1/articles`: Search and filter articles with pagination.
- `GET /api/v1/articles/{id}`: Detailed view of a specific article.
- `GET /api/v1/health`: Check API, DB, and Redis status.

---

## 📂 Project Structure

```text
app/
├── api/             # API Router and Endpoints
├── core/            # Database, Cache, and Configuration
├── models/          # SQLAlchemy Database Models
├── schemas/         # Pydantic Request/Response Models
├── services/        # Business Logic & News Source Adapters
├── tasks/           # Celery Background Jobs
└── utils/           # Shared Utilities
```

---

## 🧪 Testing

Run the test suite using `pytest`:
```bash
pytest
```

---

## 🛡️ License
This project is licensed under the MIT License.
