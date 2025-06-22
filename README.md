# Data Server API Server (ReadyAPI Version)

A modern, async Python API server for cyber threat intelligence, news, and scraping, powered by ReadyAPI, MongoDB, Elasticsearch, and Apify.

## Features
- RSS feed aggregation and cleaning
- Twitter and screenshot scraping via Apify
- Full-text and advanced search via Elasticsearch
- Stats endpoints from MongoDB
- Rate limiting, CORS, and production-ready Docker support

## Requirements
- Python 3.11+
- MongoDB instance
- Elasticsearch (Elastic Cloud recommended)
- Apify account (for scraping endpoints)
- Docker (optional, for containerized deployment)

## Setup
1. **Clone the repository**
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in your credentials:
     ```sh
     cp .env.example .env
     # Edit .env with your values
     ```

## Running the App
### Locally
```sh
uvicorn app.main:app --reload --port 5555
```

### With Docker
```sh
docker build -t data_server_api_server_py .
docker run -d --env-file .env -p 5555:5555 data_server_api_server_py
```

## API Overview
- `GET /rss-feed?source=hacker-news,graham-cluley` — Aggregated RSS feeds
- `GET /scrapper/screenshot?url=...` — Screenshot a web page via Apify
- `GET /scrapper/twitter?query=...&max_item=...` — Scrape tweets via Apify
- `POST /search/index` — Search Elasticsearch (see request body in code)
- `POST /search/index/v2` — Advanced search across monthly indices
- `POST /search/index/v3` — Custom index/query search
- `GET /stats/last-scrap-time` — Last scrape status from MongoDB
- `GET /stats/{id}` — Stats document by ID

## Environment Variables
See `.env.example` for all required variables:
- `MONGO_URI`, `MONGO_DB`
- `ELASTIC_CLOUD_ID`, `ELASTIC_CLOUD_USERNAME`, `ELASTIC_CLOUD_PASSWORD`
- `APIFY_TOKEN`

## License
MIT 