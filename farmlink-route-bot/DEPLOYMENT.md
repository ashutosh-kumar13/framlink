# FarmLink Route Bot v2.0 - Deployment Guide

## Quick Start

### 1. Prerequisites
- Python 3.11+
- pip package manager
- Windows/Linux/macOS

### 2. Installation

```powershell
# Clone or navigate to project directory
cd farmlink-route-bot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1          # Windows
# source .venv/bin/activate           # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test the API

```powershell
# Open interactive docs
# Navigate to: http://127.0.0.1:8000/docs

# Or run sample request
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/optimize `
  -ContentType 'application/json' `
  -InFile sample_request.json | ConvertTo-Json -Depth 10
```

---

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY sample_request.json .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t farmlink-route-bot:2.0 .
docker run -p 8000:8000 farmlink-route-bot:2.0
```

### Environment Variables

```bash
# .env file
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
OSRM_BASE_URL=https://router.project-osrm.org
ROUTING_PROFILE=driving

# For production, use self-hosted OSRM:
# OSRM_BASE_URL=https://routing.your-domain.com
```

### Production Server (Gunicorn + Nginx)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers, 2 threads each)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app

# Nginx reverse proxy (nginx.conf)
upstream farmlink_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.farmlink.example.com;

    location / {
        proxy_pass http://farmlink_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for optimization requests
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## Monitoring & Logging

### Health Checks

```bash
# Simple health check
curl http://127.0.0.1:8000/health

# Detailed health check with weather
curl -X POST http://127.0.0.1:8000/health-check \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

### Response Logging

Modify `app.py` to add logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/optimize")
async def optimise(request: OptimiseRequest) -> dict:
    logger.info(f"Optimization request: {len(request.orders)} orders, {len(request.vehicles)} vehicles")
    # ... rest of function
    logger.info(f"Optimization complete: {len(result['routes'])} routes generated")
    return result
```

### Performance Monitoring

Typical metrics:
- **Request Time**: 1-5 seconds (depending on order count)
- **Memory**: ~200MB baseline + 50MB per 100 orders
- **CPU**: Single request uses 1-2 cores (multi-threaded)

---

## Scaling Considerations

### For 10-50 Orders
- Single instance sufficient
- 2GB RAM, 1-2 CPU cores
- Direct OSRM/Open-Meteo APIs

### For 50-500 Orders
- Consider load balancer
- Cache weather data (1-hour TTL)
- Batch optimization requests
- Self-hosted OSRM recommended

### For 500+ Orders
- Horizontal scaling with load balancer
- Message queue (Redis/RabbitMQ) for async optimization
- Dedicated weather/routing microservices
- Database for caching routes and historical data

---

## API Rate Limiting

Recommended limits:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/optimize")
@limiter.limit("100/minute")
async def optimise(request: OptimiseRequest, request_obj = Request) -> dict:
    # ... function body
```

---

## Error Handling & Fallbacks

The bot gracefully handles failures:

1. **Weather API Down**: Uses fallback weather (safe conditions)
2. **OSRM Down**: Falls back to Haversine distance estimates
3. **No Feasible Route**: Returns 422 with clear error message
4. **Invalid Input**: Returns 400 with validation details

---

## Troubleshooting

### "No feasible route" Error

**Cause**: Vehicles too small or orders too large

**Solution**:
```json
// Increase vehicle capacity
"vehicles": [
  {"id": "truck-1", "capacity_kg": 1000},  // was 700
  {"id": "truck-2", "capacity_kg": 700}
]
```

### Slow Optimization (>10 seconds)

**Cause**: Too many orders or complex problem

**Solution**:
- Reduce time limit (modify `parameters.time_limit.seconds`)
- Use simpler heuristic (change `PARALLEL_CHEAPEST_INSERTION`)
- Split into smaller regional problems

### Weather Not Updating

**Cause**: Weather API rate limited or unavailable

**Solution**:
- Check `WEATHER_API_URL` environment variable
- Verify internet connectivity
- Check Open-Meteo status: https://status.open-meteo.com

---

## Backup & Recovery

### Database Backup (if using)

```bash
# Export completed routes
sqlite3 farmlink.db "SELECT * FROM routes;" > routes_backup.csv

# Monthly archive
tar -czf routes_backup_$(date +%Y%m).tar.gz routes_backup.csv
```

### Config Backup

```bash
# Backup environment and settings
cp .env .env.backup
```

---

## Support & Debugging

### Enable Debug Mode

```python
app = FastAPI(
    title="FarmLink Route Bot",
    version="2.0.0",
    debug=True  # Show full error traces
)
```

### API Documentation

- Interactive Docs: http://your-domain:8000/docs
- ReDoc: http://your-domain:8000/redoc

### Common Status Codes

- **200**: Successful optimization
- **400**: Invalid request format
- **422**: No feasible solution
- **500**: Server error (check logs)
- **503**: External API unavailable (fallback active)

---

## Performance Optimization Tips

### 1. Cache Weather Data
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=256)
async def cached_weather(lat: float, lon: float) -> Weather:
    # Cache for 10 minutes
    return await weather_at(client, Location(name="", latitude=lat, longitude=lon))
```

### 2. Batch Optimize
Instead of individual requests, batch multiple orders:
```json
// Good: Single batch
{"depot": {}, "vehicles": [3], "orders": [50]}

// Avoid: Many individual requests
{"depot": {}, "vehicles": [1], "orders": [2]} × 25 times
```

### 3. Use Connection Pooling
```python
# Reuse OSRM/Weather connections
async with httpx.AsyncClient(timeout=12.0, limits=Limits(max_connections=20)) as client:
    # Make multiple requests
```

---

## Security Best Practices

### 1. Validate Input
```python
# Already built-in via Pydantic
@app.post("/optimize")
async def optimise(request: OptimiseRequest) -> dict:
    # Automatically validates all fields
```

### 2. Rate Limiting
```python
# Prevent abuse
limiter.limit("1000/hour")(route_function)
```

### 3. HTTPS/TLS
```bash
# Use SSL certificates in production
uvicorn app:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### 4. API Keys (Optional)
```python
from fastapi import Header, HTTPException

@app.post("/optimize")
async def optimise(request: OptimiseRequest, x_token: str = Header()) -> dict:
    if x_token != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... proceed
```

---

## Maintenance Schedule

### Daily
- Monitor error logs
- Check API response times

### Weekly
- Review weather data accuracy
- Validate route completion rates

### Monthly
- Backup database/configs
- Update Python packages (`pip list --outdated`)
- Review performance metrics

### Quarterly
- Retrain ML models with new data
- Update hazard detection thresholds
- Security audit

---

## Support

For issues or questions:
1. Check logs: `app.log`
2. Review FEATURES_GUIDE.md for feature details
3. Test with sample_request.json
4. Check Open-Meteo/OSRM status pages
5. Enable debug mode for detailed errors
