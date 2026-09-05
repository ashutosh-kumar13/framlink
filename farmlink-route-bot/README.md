# FarmLink Route Bot v2.0

Advanced weather-aware and disaster-resilient route optimization for farmer logistics. Now with natural hazard detection, dynamic risk assessment, and enhanced driver safety features.

## Key Features (v2.0)

### 🌦️ Enhanced Weather Intelligence
- **Real-time weather integration** via Open-Meteo API (precipitation, wind, temperature, humidity, visibility)
- **Weather multipliers** that adjust route times based on actual conditions
- **Seasonal hazard detection** (flooding, landslides, hail, extreme heat, fog)
- **Risk level classification** (Safe → Caution → Warning → Dangerous)

### 🚨 Natural Disaster Management
- **Automatic hazard detection** for:
  - Flooding (high rainfall + low elevation)
  - Landslides (high rainfall + high elevation)
  - Hail/Thunderstorms (weather codes 80-86)
  - Extreme heat (>45°C)
  - Strong winds (>40 km/h)
  - Poor visibility (<1 km)
- **Location-aware risk assessment** using elevation data
- **Hazard recommendations** for drivers with actionable instructions

### 👨‍🚗 Driver-Friendly Route Display
- **Real-time weather alerts** at each stop with severity levels
- **Visual hazard indicators** showing all detected natural obstacles
- **Estimated arrival times** accounting for weather delays
- **Load progression** showing vehicle capacity through route
- **Driver instructions** with safety recommendations
- **Hazard summary** per route with frequency counts

### 🧠 AI Priority Scoring (v2.0)
Enhanced transparent scoring considering:
- Crop perishability (1-5 scale)
- Weather hazard count and precipitation
- Temperature stress on cold-storage crops
- Delivery deadline urgency
- Natural disaster risk levels
- Explanatory reasons for each priority

### 📦 Smart Optimization
- Google OR-Tools capacitated vehicle routing with time windows
- Pickup-before-delivery constraints
- Weather-adjusted travel times
- Perishability-weighted scheduling
- Fallback to haversine estimates (OSRM unavailable)

## Architecture

```
Request → Weather API → Hazard Detection
        → OSRM Routing → Distance/Time Matrix
        ↓
    OR-Tools Solver (5s search)
        ↓
Enhanced Route Cards → Driver UI
        ↓
AI Priority Rankings → Dispatcher Dashboard
```

## What it Optimises

Every route observes:
- **Vehicle capacity** constraints
- **Pickup→Delivery sequencing** per order
- **Weather-adjusted travel time** with safety buffers
- **Hazard-based alternative routing** recommendations
- **Perishable produce prioritisation** accounting for weather risk
- **Driver safety** with real-time hazard alerts

The response includes:
- Baseline and weather-adjusted distance/time estimates
- Weather alerts and natural hazard warnings per stop
- Priority scores with detailed reasoning
- Driver-friendly route cards with navigation
- Hazard summary for route planning

## Setup

Use Python 3.11+.

```powershell
cd farmlink-route-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the interactive API.

## Environment Variables

Optional; defaults use public demo endpoints.

```text
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
OSRM_BASE_URL=https://router.project-osrm.org
ROUTING_PROFILE=driving
```

For production, host your own OSRM service and use a weather provider with appropriate SLAs.

## API Endpoints

- `GET /health` - Simple service status check
- `POST /health-check` - Detailed health with sample weather fetch
- `POST /optimize` - Full weather-aware, hazard-informed optimization

## Request Schema (v2.0)

```json
{
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
        "name": "Kothrud Retailer",
        "latitude": 18.5074,
        "longitude": 73.8077,
        "elevation_m": 580,
        "state_code": "MH"
      }
    }
  ]
}
```

## Response Example (v2.0)

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
          "load_before_kg": 0,
          "load_after_kg": 0,
          "estimated_arrival_minutes": 0,
          "weather": {
            "rain_mm": 5.2,
            "wind_kmh": 35,
            "temperature_c": 28,
            "humidity_percent": 65,
            "visibility_km": 8.5,
            "risk_level": "caution",
            "hazards": ["heavy_rain", "strong_wind"]
          },
          "alert": {
            "severity": "caution",
            "message": "Weather alert: heavy_rain, strong_wind",
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

## Run the Sample

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/optimize -ContentType 'application/json' -InFile sample_request.json
```

## Adding a Real ML Model

`priority_score` is transparent by design. Once you collect completed-order data (crop, quantity, market price, demand, delivery time, weather, spoilage outcome), replace `ai_priority_score` with a trained XGBoost/Prophet/LightGBM model.

**Keep these features:**
- Perishability
- Weather hazards & precipitation
- Temperature stress
- Delivery urgency
- Risk levels

These provide the strongest signal for spoilage and customer satisfaction.

## Hazard Risk Levels

| Level | Multiplier | Driver Action |
|-------|-----------|---------------|
| **SAFE** | 0% | Normal operations |
| **CAUTION** | 15% | Monitor conditions; buffer time |
| **WARNING** | 40% | Reduce speed; extra caution |
| **DANGEROUS** | 80% | Postpone non-urgent; alternative routes |

## Future Enhancements

- [ ] Historical spoilage data integration
- [ ] Real-time traffic incident API
- [ ] Multi-modal routing (rail, air, sea)
- [ ] Cold-chain temperature monitoring
- [ ] Driver SOS + damage reporting
- [ ] Carbon footprint optimization
- [ ] Blockchain delivery verification
