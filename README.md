# 📰 Pulse - Modern News Aggregator

A production-ready, high-performance **Progressive Web App (PWA)** news aggregator built with **FastAPI**, **PostgreSQL**, and **Celery**. This system automatically fetches, deduplicates, and serves news articles from multiple global sources with a stunning, modern UI.

---

## ✨ Key Features

### 🎯 Core Functionality
- **Async Architecture**: Built with `FastAPI` and `SQLAlchemy 2.0` with `asyncpg` for non-blocking I/O
- **Multi-Source Integration**: 
  - [NewsAPI.org](https://newsapi.org/)
  - [The Guardian](https://open-platform.theguardian.com/)
  - [New York Times](https://developer.nytimes.com/)
- **Background Tasks**: Scheduled ingestion using `Celery` and `Redis`
- **Intelligent Deduplication**: SHA256 URL hashing prevents duplicate articles
- **High-Performance Search**: PostgreSQL `GIN` indexes and `pg_trgm` for fast full-text search
- **Caching Layer**: Redis-based caching for sub-millisecond response times

### 🧠 Intelligence Layer
- **Read Time Estimation**: Smart calculation based on article length with truncation detection
- **Sentiment Analysis**: Keyword-based classification (Positive, Neutral, Urgent)
- **Visual Badges**: Color-coded, animated badges for quick article insights

### 📱 Modern UX
- **Infinite Scroll**: Twitter/Instagram-style seamless content loading
- **Progressive Web App (PWA)**: 
  - Installable on mobile and desktop
  - Offline-ready with service worker caching
  - Native app-like experience
  - Custom app icon and splash screen
- **Bookmark System**: Save articles locally with localStorage (no auth required)
  - Star icon with smooth animations
  - Dedicated "Saved" view with filtering
  - Limit of 50 saved articles
- **Dark/Light Mode**: Premium glassmorphic design with theme persistence
- **Responsive Design**: Optimized for mobile, tablet, and desktop

### 🎨 Premium UI/UX
- **Glassmorphism Design**: Modern, translucent card-based interface
- **Custom Dropdown**: Sleek news source selector
- **Smooth Animations**: Micro-interactions and transitions throughout
- **Modal Article View**: Distraction-free reading experience with hidden scrollbars
- **Custom Icons**: AI-generated Pulse branding

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async driver
- **Task Queue**: Celery + Redis
- **Cache**: Redis
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic

### Frontend
- **Core**: Vanilla HTML, CSS, JavaScript
- **PWA**: Service Worker, Web App Manifest
- **Fonts**: Google Fonts (Outfit, Playfair Display)
- **Icons**: Font Awesome 6.5.1
- **Storage**: localStorage for bookmarks

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js (optional, for frontend tooling)

### 1. Clone & Environment
Rename `.env.example` to `.env` and fill in your API keys:
```bash
# PostgreSQL
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/newsaggregator"

# Redis
REDIS_URL="redis://localhost:6379/0"
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/2"

# API Keys
NEWSAPI_KEY="your_newsapi_key"
GUARDIAN_API_KEY="your_guardian_key"
NYTIMES_API_KEY="your_nytimes_key"
```

### 2. Run with Docker (Recommended)
This starts the API, PostgreSQL, Redis, and Celery workers in one command:
```bash
docker-compose up --build
```

### 3. Run Locally (Windows)
If you have PostgreSQL and Redis running locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run database migrations**:
   ```bash
   python -m alembic upgrade head
   ```

3. **Launch all services**:
   ```bash
   .\run_local.bat
   ```
   This starts:
   - FastAPI server (port 8000)
   - Celery worker
   - Celery beat scheduler
   - Frontend (served via Python HTTP server on port 3000)

---

## 🎨 Frontend Features

The `/frontend` directory contains a modern, production-ready PWA with:

### User Features
- **Infinite Scroll**: Automatically loads more articles as you scroll
- **Smart Search**: Real-time search with debouncing
- **Multi-Filter**: Category and source filtering
- **Bookmark System**: Save articles for later with visual star icons
- **Theme Toggle**: Persistent dark/light mode
- **Intelligence Badges**: Read time and sentiment indicators

### PWA Capabilities
- **Installable**: Add to home screen on mobile/desktop
- **Offline Support**: Cached app shell for instant loading
- **Fast Loading**: Service worker caching strategy
- **Native Feel**: Standalone display mode, custom theme colors

### Technical Highlights
- **Intersection Observer**: Efficient infinite scroll implementation
- **Cache Busting**: Versioned CSS for reliable updates
- **Custom Dropdown**: Fully styled, accessible source selector
- **Modal System**: Smooth article preview with backdrop blur

Access the frontend at: [http://localhost:3000](http://localhost:3000)

---

## 📖 API Documentation

Once the app is running, access the interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Articles
- `GET /api/v1/articles`: Search and filter articles with pagination
  - Query params: `q` (search), `source`, `category`, `page`, `page_size`
  - Returns: Paginated results with total count and page info
- `GET /api/v1/articles/{id}`: Get detailed article by ID
- `POST /api/v1/sync`: Trigger manual news fetch (background task)

#### Health & Status
- `GET /api/v1/health`: Check API, database, and Redis connectivity

---

## 📂 Project Structure

```text
News Aggregator/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # API route handlers
│   ├── core/                   # Database, cache, config
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/
│   │   ├── news_sources/       # Source adapters (NewsAPI, Guardian, NYT)
│   │   ├── article_service.py  # Article business logic
│   │   └── intelligence_service.py  # Read time & sentiment
│   ├── tasks/                  # Celery background tasks
│   └── main.py                 # FastAPI application entry
├── frontend/
│   ├── index.html              # Main HTML
│   ├── style.css               # Glassmorphic styling
│   ├── app.js                  # Frontend logic
│   ├── manifest.json           # PWA manifest
│   ├── sw.js                   # Service worker
│   └── icon.png                # App icon
├── alembic/                    # Database migrations
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker orchestration
└── run_local.bat               # Windows launcher script
```

---

## 🔄 Background Tasks

### Celery Tasks
- **`fetch_all_sources`**: Fetches latest articles from all configured sources
  - Runs every 30 minutes (configurable in Celery Beat)
  - Handles errors gracefully per source
  - Returns summary of articles added

### Manual Sync
Trigger immediate fetch via:
```bash
POST /api/v1/sync
```
Or use the "Sync" button in the frontend UI.

---

## 🧪 Testing

Run the test suite using `pytest`:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=app --cov-report=html
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY` in environment
- [ ] Use production-grade PostgreSQL instance
- [ ] Configure Redis persistence
- [ ] Set up HTTPS (required for full PWA features)
- [ ] Enable CORS for your domain
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure log aggregation
- [ ] Set up automated backups

### Recommended Platforms
- **Backend**: Railway, Render, DigitalOcean App Platform
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: Supabase, Railway, Neon
- **Redis**: Upstash, Redis Cloud

---

## 🎯 Roadmap

- [ ] User authentication & personalization
- [ ] Article recommendations (ML-based)
- [ ] Email digest subscriptions
- [ ] Social sharing integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] RSS feed generation
- [ ] Browser extension

---

## 🛡️ License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **News Sources**: NewsAPI, The Guardian, New York Times
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Outfit, Playfair Display)
- **Design Inspiration**: Modern glassmorphism trends

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

**Built with ❤️ using FastAPI and modern web technologies**
