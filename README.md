# Content Moderation System

A **scalable content moderation system** using **FastAPI, Celery, Redis, PostgreSQL, and Docker** that integrates with **OpenAI’s moderation API** for text content filtering. The system supports **caching, task queues, monitoring, and structured logging**.

---

## Features

- **FastAPI for APIs**
- **Celery with Redis** for asynchronous task processing
- **PostgreSQL** for storing moderation results
- **Caching with Redis**
- **Monitoring with Prometheus & Grafana**
- **Logging with structlog**
- **Dockerized for easy deployment**

---

## Installation & Setup

### **1 Clone the Repository**
```bash
git clone https://github.com/kimforee/content-moderation.git
cd content-moderation
```

### **2 Create an Environment File**
Create a `.env` file in the root directory and add (.env_example for reference):
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/moderation
REDIS_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO
MAX_WORKERS=4
ENVIRONMENT=development
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
CACHE_TTL=3600
```

### **3 Start the Application with Docker**
```bash
docker-compose up --build
```

This will start:
- FastAPI on `http://localhost:8000`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3000`
- RabbitMQ on `http://localhost:15672`
---

## API Endpoints

### **1 Moderate Text**
```http
POST /api/v1/moderate/text
```
**Request:**
```json
{
  "content": "Some text to moderate"
}
```
**Response:**
```json
{
  "id": 1,
  "content": "Some text to moderate",
  "flagged": false,
  "categories": []
}
```

### **2 Get Moderation Result**
```http
GET /api/v1/moderation/{id}
```

### **3 Health Check**
```http
GET /health
```
**Response:**
```json
{
  "status": "ok"
}
```

### **4 Metrics for Monitoring**
```http
GET /metrics
```
---

## Monitoring
- **Prometheus** is running at `http://localhost:9090`
- **Grafana** is available at `http://localhost:3000` (default credentials: `admin/admin`)

---

## Running Tests
```bash
poetry run pytest
```

---

## Performance Considerations
- **Caching with Redis** reduces OpenAI API calls.
- **Celery task queues** handle high throughput.
- **Rate limiting** prevents abuse.
- **Database indexing** improves query speed.

---

## License
MIT License. See `LICENSE` for details.

