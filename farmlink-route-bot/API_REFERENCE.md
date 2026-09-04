# FarmLink Route Bot v2.0 - API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. GET /health
Simple health check endpoint.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200):**
```json
{
  "status": "ok",
  "service": "FarmLink Route Bot"
}
```

---

### 2. POST /health-check
Detailed health check with sample weather fetch and API validation.

**Request:**
```bash
curl -X POST http://localhost:8000/health-check \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

**Response (200):**
```json
{
  "status": "operational",
  "weather_api": "available",
  "routing_api": "available",
  "sample_weather": {
    "depot": {
      "rain_mm": 0.0,
      "wind_kmh": 15.5,
      "temperature_c": 28.3,
      "humidity_percent": 65,
      "visibility_km": 10.0,
      "weather_code": 0,
      "risk_level": "safe",
      "hazards": [],
      "source": "open-meteo"
    },
    "hazards_detected": false
  }
}
```

**Response (Degraded):**
```json
{
  "status": "degraded",
  "error": "Connection timeout",
  "message": "Using fallback services"
}
```

---

### 3. POST /optimize
Main endpoint for route optimization with weather and hazard awareness.

**Request:**
```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "depot": {
      "name": "Pune FPO Hub",
      "latitude": 18.5204,
      "longitude": 73.8567,
      "elevation_m": 560,
      "state_code": "MH"
    },
    "vehicles": [
      {
        "id": "truck-1",
        "capacity_kg": 700
      }
    ],
    "orders": [
      {
        "id": "ORD-101",
        "crop": "Tomato",
        "quantity_kg": 240,
        "perishability": 5,
        "storage_temp_c": 12,
        "promised_delivery_hours": 12,
        "pickup": {
          "name": "Ramesh Farm",
          "latitude": 18.6279,
          "longitude": 73.7932,
          "elevation_m": 650,
          "state_code": "MH"
        },
        "delivery": {
          "name": "Retailer",
          "latitude": 18.5074,
          "longitude": 73.8077,
          "elevation_m": 580,
          "state_code": "MH"
        }
      }
    ]
  }'
```

**Response (200):**
```json
{
  "routes": [
    {
      "vehicle_id": "truck-1",
      "distance_km": 45.3,
      "weather_adjusted_minutes": 125.5,
      "overall_risk": "caution",
      "hazard_summary": {
        "heavy_rain": 2,
        "strong_wind": 1
      },
      "driver_instructions": "ℹ️ Monitor weather; minor delays possible | 📍 4 stops | ⏱️ 126 min | 📦 Max load: 240kg",
      "stops": [
        {
          "stop": "Pune FPO Hub",
          "latitude": 18.5204,
          "longitude": 73.8567,
          "kind": "depot",
          "order_id": null,
          "crop": null,
          "load_before_kg": 0,
          "load_after_kg": 0,
          "estimated_arrival_minutes": 0,
          "weather": {
            "rain_mm": 5.2,
            "wind_kmh": 35.0,
            "temperature_c": 28.0,
            "humidity_percent": 65,
            "visibility_km": 8.5,
            "weather_code": 61,
            "risk_level": "caution",
            "hazards": ["heavy_rain", "strong_wind"],
            "source": "open-meteo"
          },
          "alert": {
            "severity": "caution",
            "message": "Weather alert: heavy_rain, strong_wind",
            "hazards": ["heavy_rain", "strong_wind"],
            "recommendation": "Monitor weather; consider adding buffer time"
          }
        }
      ]
    }
  ],
  "summary": {
    "total_distance_km": 125.8,
    "weather_adjusted_minutes": 356.2,
    "served_orders": 3
  },
  "ai_priorities": [
    {
      "order_id": "ORD-101",
      "crop": "Tomato",
      "priority_score": 85,
      "reason": "Priority: highly perishable; weather risk at pickup (caution); tight deadline",
      "pickup_risk": "caution",
      "delivery_risk": "safe"
    }
  ],
  "data_sources": {
    "routing": "osrm",
    "weather": ["open-meteo"]
  },
  "api_version": "2.0.0-enhanced"
}
```

**Errors:**

422 - No feasible route:
```json
{
  "detail": "No feasible route. Add vehicle capacity or reduce order quantities."
}
```

400 - Invalid input:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "orders", 0, "quantity_kg"],
      "msg": "ensure this value is greater than 0"
    }
  ]
}
```

---

## Data Models

### Location
```json
{
  "name": "string (required)",
  "latitude": "float (-90 to 90, required)",
  "longitude": "float (-180 to 180, required)",
  "elevation_m": "int (default: 0)",
  "state_code": "string (default: '')"
}
```

### Vehicle
```json
{
  "id": "string (required, unique)",
  "capacity_kg": "int (required, > 0)"
}
```

### Order
```json
{
  "id": "string (required, unique)",
  "crop": "string (required)",
  "quantity_kg": "int (required, > 0)",
  "perishability": "int (1-5, default: 3)",
  "storage_temp_c": "int (default: 15)",
  "promised_delivery_hours": "float (> 0, default: 24)",
  "pickup": "Location (required)",
  "delivery": "Location (required)"
}
```

### Weather
```json
{
  "rain_mm": "float (default: 0)",
  "wind_kmh": "float (default: 0)",
  "temperature_c": "float (default: 25)",
  "humidity_percent": "int (default: 50)",
  "visibility_km": "float (default: 10)",
  "weather_code": "int (WMO code, default: 0)",
  "risk_level": "string (safe|caution|warning|dangerous)",
  "hazards": "string[] (flooding|landslide|heavy_rain|strong_wind|hail|extreme_heat|road_closure|fog)",
  "source": "string (open-meteo|fallback)"
}
```

### RouteStop
```json
{
  "stop": "string",
  "latitude": "float",
  "longitude": "float",
  "kind": "string (depot|pickup|delivery)",
  "order_id": "string | null",
  "crop": "string | null",
  "load_before_kg": "int",
  "load_after_kg": "int",
  "estimated_arrival_minutes": "int",
  "weather": "Weather",
  "alert": "DriverAlert | null"
}
```

### DriverAlert
```json
{
  "severity": "string (safe|caution|warning|dangerous)",
  "message": "string",
  "hazards": "string[]",
  "recommendation": "string"
}
```

### RouteCard
```json
{
  "vehicle_id": "string",
  "distance_km": "float",
  "weather_adjusted_minutes": "float",
  "overall_risk": "string",
  "hazard_summary": "object (hazard_name: count)",
  "driver_instructions": "string",
  "stops": "RouteStop[]"
}
```

---

## Perishability Scale

| Level | Crop Examples | Days | Notes |
|-------|--------------|------|-------|
| **1** | Potatoes, Onions | 30-90 | Highly durable, long storage |
| **2** | Carrots, Cabbage | 14-30 | Moderate durability |
| **3** | Tomatoes, Peppers | 7-14 | Standard perishable |
| **4** | Bananas, Mangoes | 3-7 | Highly perishable |
| **5** | Berries, Lettuce | 1-3 | Extremely perishable, refrigeration needed |

---

## Risk Levels & Actions

| Level | Color | Multiplier | Driver Action | Example |
|-------|-------|-----------|---|---------|
| **SAFE** | 🟢 | 0% | Normal | Clear skies, <25 km/h wind |
| **CAUTION** | 🟡 | 15% | Monitor | 10-20mm rain, 25-40 km/h wind |
| **WARNING** | 🟠 | 40% | Be cautious | 20-30mm rain, 40-60 km/h wind |
| **DANGEROUS** | 🔴 | 80% | Avoid | >30mm + flood risk, >60 km/h wind, hail |

---

## Weather Codes (WMO)

Common codes returned by API:

| Code | Condition |
|------|-----------|
| 0 | Clear sky |
| 1-2 | Mainly clear, partly cloudy |
| 3 | Overcast |
| 45 | Foggy |
| 48 | Foggy/rime |
| 51-57 | Drizzle (light to moderate) |
| 61-67 | Rain (slight to heavy) |
| 71-77 | Snow |
| 80-82 | Rain showers |
| 85-86 | Snow showers |
| 95-99 | Thunderstorm |

---

## Example Workflows

### Workflow 1: Basic Optimization
```
1. POST /health-check         → Verify APIs are working
2. POST /optimize             → Get routes
3. Parse routes → sort by priority_score
4. Assign to drivers
```

### Workflow 2: Weather-Aware Dispatch
```
1. POST /optimize
2. Filter routes by overall_risk == "dangerous"
3. For dangerous routes:
   - Notify dispatcher (SMS/email)
   - Show driver_instructions in app
   - Suggest alternative timing
4. For normal routes:
   - Auto-dispatch to driver app
   - Add buffer time to ETA
```

### Workflow 3: Cold-Chain Management
```
1. Set storage_temp_c for each order
2. POST /optimize
3. Review temperature_stress in priority_score
4. Routes with high temp stress:
   - Priority first delivery (less time in vehicle)
   - Use insulated containers
   - Add ice packs
```

---

## Performance Guidelines

### Request Size
- **Optimal**: 5-20 orders per request
- **Maximum**: 100 orders (tested, takes ~5 seconds)
- **Recommended**: Batch orders by region if >50

### Response Time
- **Average**: 1-3 seconds
- **Max**: 5 seconds (OR-Tools limit)
- **Fallback**: <1 second (if using Haversine)

### Memory Usage
- **Baseline**: 200 MB
- **Per 100 orders**: +50 MB
- **Per vehicle**: +5 MB

---

## Rate Limits
Default (no authentication):
- 1000 requests/hour
- 100 requests/minute

Contact support for higher limits.

---

## Caching Strategy

Recommended client-side caching:
- **Weather data**: 10-30 minutes (conditions change slowly)
- **Route solutions**: 5-10 minutes (reoptimize as conditions change)
- **Location coordinates**: No expiry (rarely change)

---

## Error Responses

### 400 - Bad Request
```json
{
  "detail": [
    {
      "type": "validation_error",
      "loc": ["body", "orders", 0],
      "msg": "field required"
    }
  ]
}
```

### 422 - Unprocessable Entity
```json
{
  "detail": "Orders exceed every vehicle capacity: ORD-101, ORD-102"
}
```

### 500 - Server Error
```json
{
  "detail": "Internal server error. Check logs for details."
}
```

### 503 - Service Unavailable
```json
{
  "detail": "External APIs unavailable. Using fallback routing (Haversine distance estimates)."
}
```

---

## Testing with cURL

### Health Check
```bash
curl -v http://localhost:8000/health
```

### Detailed Health
```bash
curl -X POST http://localhost:8000/health-check \
  -H "Content-Type: application/json" \
  -d @sample_request.json | jq .
```

### Full Optimization
```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d @sample_request.json \
  -o response.json && cat response.json | jq .
```

### Save Response to File
```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d @sample_request.json > optimization_result.json
```

---

## WebSocket Support (Future)
Coming in v2.1:
```
ws://localhost:8000/optimize-stream
// Real-time route updates as weather changes
```

---

## Versioning
Current: **2.0.0-enhanced**
- v1.0: Basic weather-aware optimization
- v2.0: Hazard detection + driver UI + enhanced scoring
- v2.1: Real-time streaming, ML models
- v3.0: Multi-modal routing, blockchain verification
