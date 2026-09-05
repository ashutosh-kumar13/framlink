# FarmLink Route Bot v2.0 - Feature Guide

## Overview

The enhanced FarmLink Route Bot now provides **disaster-aware route optimization** with real-time weather integration and natural hazard detection. This guide explains all new features and how to use them effectively.

---

## 🌦️ Weather Integration Features

### Real-Time Weather Monitoring
- Fetches hourly weather from Open-Meteo API
- Includes: precipitation, wind speed, temperature, humidity, visibility
- Updates weather conditions for each location in real-time
- Automatic fallback to default values if API is unavailable

### Weather-Adjusted Route Times
Routes are automatically adjusted based on actual weather conditions:
- **Rainfall**: +10% time per mm (capped at 50%)
- **Wind**: +1.5% time per km/h above 25 km/h (capped at 35%)
- **Storms**: +20% time when thunderstorm detected
- **Extreme Heat**: +2% time per °C above 30°C
- **Hazards**: Additional 15-80% time based on risk level

**Example**: A 100-minute route in heavy rain with 45 km/h wind becomes ~135 minutes.

---

## 🚨 Natural Hazard Detection

### Automated Hazard Identification

The bot detects **8 types of natural obstacles** and assigns risk levels:

#### 1. **Flooding Risk** 🌊
- **Trigger**: Rainfall > 20mm
- **Severity increases if**: Location elevation < 100m
- **Risk Level**: Caution → Warning → Dangerous
- **Impact**: 40-80% route delay

#### 2. **Landslide Risk** ⛰️
- **Trigger**: Rainfall > 30mm + Elevation > 300m
- **Auto-classified as**: DANGEROUS
- **Recommended Action**: Consider alternative routes

#### 3. **Heavy Rain** 🌧️
- **Trigger**: Rainfall > 10mm
- **Causes**: 5-50% time increase
- **Driver Alert**: Automatic visibility reduction warning

#### 4. **Strong Wind** 💨
- **High Risk**: > 60 km/h (DANGEROUS)
- **Moderate**: 40-60 km/h (WARNING)
- **Minor**: 25-40 km/h (included in normal delays)
- **Impact**: Affects vehicle stability and handling

#### 5. **Hail Storms** ❄️
- **Detection**: Weather codes 80-86 (thunderstorm/hail)
- **Risk Level**: WARNING or DANGEROUS
- **Recommendation**: Seek shelter; delay non-urgent deliveries

#### 6. **Extreme Heat** 🔥
- **Trigger**: Temperature > 45°C
- **Impact**: Driver fatigue; produce spoilage risk
- **Risk Level**: WARNING
- **Mitigation**: Extra cooling time for cold-storage

#### 7. **Poor Visibility/Fog** 🌫️
- **Trigger**: Visibility < 1 km
- **Risk Level**: CAUTION
- **Impact**: Slower vehicle speeds; accident risk

#### 8. **Road Closure** 🚫
- **Marker**: Reserved for future integration with road data APIs
- **Current**: Defaults to safe if not detected

---

## 📊 Risk Level Classification

Each location receives a **risk level** that propagates through route planning:

| Risk Level | Multiplier | Visibility | Driver Action | Recommendation |
|-----------|-----------|-----------|---------------|--------------|
| **SAFE** | 0% | Green ✅ | Normal | Proceed with standard delivery times |
| **CAUTION** | 15% | Yellow ⚠️ | Monitor conditions | Add 15% buffer; watch weather updates |
| **WARNING** | 40% | Orange ⚠️ | Reduce speed | Add 40% buffer; consider delay |
| **DANGEROUS** | 80% | Red 🚫 | Avoid route | Consider postponing; alternative routing |

---

## 🧠 Enhanced Priority Scoring System (v2.0)

### Priority Score Calculation

Each order receives a **0-100 priority score** based on:

```
Score = Perishability (×15) 
      + Hazard Risk (×8 per hazard + rain)
      + Temperature Stress
      + Quantity/Value (up to 15)
      + Late Delivery Penalty (if deadline < 24h)
      + Risk Bonus (0-25 based on max risk level)
```

### Example Priority Scenarios

**HIGH PRIORITY (80+)**
```
Tomato delivery (Perishability 5)
- Crop: Highly perishable
- Pickup Weather: Heavy rain + flooding risk
- Delivery Deadline: 8 hours
- Score: 85/100
- Action: Prioritize first in route queue
```

**MEDIUM PRIORITY (50-70)**
```
Onion delivery (Perishability 2)
- Crop: Moderately durable
- Weather: Caution level at delivery
- Deadline: 24 hours
- Score: 62/100
- Action: Schedule after high-priority items
```

**LOW PRIORITY (30-50)**
```
Potato delivery (Perishability 1)
- Crop: Very durable, long shelf life
- Weather: Safe conditions
- Deadline: 48 hours
- Score: 35/100
- Action: Fill remaining route capacity
```

---

## 👨‍🚗 Driver-Friendly Route Display

### Route Card Components

Each driver receives a comprehensive **route card** with:

#### 1. **Route Summary**
- Vehicle ID and capacity
- Total distance (km)
- Weather-adjusted travel time (minutes)
- Overall risk level for entire route
- Hazard frequency summary

#### 2. **Driver Instructions**
Contextual safety guidance:
- **DANGEROUS**: "⚠️ DANGEROUS CONDITIONS - Consider postponing non-urgent deliveries"
- **WARNING**: "⚠️ WARNING CONDITIONS - Drive carefully, allow extra time"
- **CAUTION**: "ℹ️ Monitor weather; minor delays possible"
- Plus: Stop count, duration, and max load info

#### 3. **Per-Stop Details**
Each stop includes:
- **Location**: Name, coordinates (lat/long)
- **Type**: Pickup, Delivery, or Depot
- **Order Info**: Order ID, Crop type
- **Load Status**: kg before/after this stop
- **Estimated Arrival**: Time from route start (minutes)
- **Weather Data**:
  - Temperature, rainfall, wind speed
  - Humidity, visibility
  - Risk level (Safe/Caution/Warning/Dangerous)
- **Alert**: If hazard detected:
  - Severity badge
  - Hazard types
  - Specific recommendation

### Example Driver Interface Output

```
┌─ TRUCK-1 ──────────────────────────────────────────┐
│ 🟡 Route: 45.3 km | 125 min | Risk: CAUTION       │
│ ⚠️ Monitor weather; minor delays possible          │
│ 📍 4 stops | 📦 Max load: 240kg                    │
├─────────────────────────────────────────────────────┤
│ STOP 1: Pune FPO Hub (DEPOT) - ETA: 0 min         │
│  ⚪ 0kg → 240kg | Weather: 28°C, 5mm rain         │
│                                                     │
│ STOP 2: Ramesh Farm (PICKUP) - ETA: 18 min        │
│  ✓ Order ORD-101 (Tomato, 240kg)                  │
│  ⚠️ 0kg → 240kg | Weather: 26°C, 8mm rain         │
│  Alert: ⚠️ CAUTION - heavy_rain, strong_wind     │
│  → Monitor weather; consider adding buffer time   │
│                                                     │
│ STOP 3: Kothrud Retailer (DELIVERY) - ETA: 52 min │
│  ✓ Deliver ORD-101 (240kg Tomato)                 │
│  📦 240kg → 0kg | Weather: 28°C, safe             │
│                                                     │
│ STOP 4: Return to Depot - ETA: 125 min            │
│  ⚪ 0kg | Safe conditions                          │
└─────────────────────────────────────────────────────┘
```

---

## 📍 Location Enhancements

### New Location Fields

Each location (depot, pickup, delivery) now includes:

```json
{
  "name": "Farm Name",
  "latitude": 18.6279,
  "longitude": 73.7932,
  "elevation_m": 650,      // NEW: Meters above sea level
  "state_code": "MH"       // NEW: State/region code
}
```

**Why elevation matters:**
- **Flooding risk**: Low elevation + heavy rain = DANGEROUS
- **Landslide risk**: High elevation + rainfall = DANGEROUS  
- **Route viability**: High-elevation routes may be blocked in storms

---

## 🌾 Crop Temperature Management

### Cold-Storage Crops

Crops with special storage requirements now get **temperature stress scoring**:

```json
{
  "crop": "Strawberry",
  "perishability": 5,
  "storage_temp_c": 4       // NEW: Optimal storage temperature
}
```

**Temperature Stress Calculation:**
- If `storage_temp_c < 10°C` (cold storage needed)
- Score increases by `(|current_temp - storage_temp| × 0.5)` per location

**Example**:
- Strawberry needs 4°C storage
- Pickup: 26°C (22°C stress)
- Delivery: 28°C (24°C stress)
- Total stress penalty: ~46 points → Higher priority

---

## ⏰ Delivery Deadline Handling

### Promised Delivery Times

Orders now track **promised delivery deadlines**:

```json
{
  "order_id": "ORD-101",
  "promised_delivery_hours": 12      // NEW: Deadline in hours
}
```

**Impact on Priority:**
- Deadline < 12 hours: +5 points per hour reduction
- Perishable + tight deadline: Highest priority
- Used to activate late-delivery penalties

**Example**:
- Tomato (perishability 5, 8-hour deadline)
- Penalty: 5 × (24-8) = 80 points base
- Plus weather risk and hazards
- Result: Often 85-90 priority score

---

## 🔧 API Response Structure (v2.0)

### Complete Response Example

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
            "wind_kmh": 35,
            "temperature_c": 28,
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
    },
    {
      "order_id": "ORD-103",
      "crop": "Strawberry",
      "priority_score": 78,
      "reason": "Priority: highly perishable; cold storage needed; tight deadline",
      "pickup_risk": "safe",
      "delivery_risk": "safe"
    },
    {
      "order_id": "ORD-102",
      "crop": "Onion",
      "priority_score": 42,
      "reason": "Standard priority",
      "pickup_risk": "safe",
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

---

## 🎯 Use Cases & Workflows

### Scenario 1: Monsoon Season Delivery

**Input:**
- Tomato order (perishable, 12-hour deadline)
- Heavy rainfall (35mm), high wind (50 km/h)
- Low elevation pickup (80m above sea level)

**Bot Response:**
- Risk Level: WARNING → "Flooding risk detected"
- Time Multiplier: 1.50× (35mm rain + wind)
- Priority Score: 92/100
- Driver Alert: "CAUTION - Flooding risk at pickup location. Route through elevated areas if possible."

**Recommendation:** 
- Dispatcher sees HIGH priority
- Route as first delivery or postpone to next day
- Driver gets 50% buffer time added

---

### Scenario 2: Mixed Delivery with Cold-Storage Crop

**Input:**
- Strawberry (perishability 5, storage 4°C) + Onion (perishability 2) 
- Clear weather, 32°C temperature
- Both have 12-hour deadline

**Bot Response:**
- Strawberry Priority: 85/100 (perishability + cold stress + deadline)
- Onion Priority: 42/100 (durable + normal deadline)

**Route Plan:**
1. Strawberry pickup (1st - no delay allowed)
2. Strawberry delivery (2nd - minimize spoilage)
3. Onion pickup (3rd)
4. Onion delivery (4th)

---

### Scenario 3: Hail Storm Avoidance

**Input:**
- 3 orders across region
- Hail storm (weather code 85) predicted at one location
- Wind 65 km/h (DANGEROUS)

**Bot Response:**
- Location with hail: Risk = DANGEROUS
- Time multiplier: 1.95× (includes 80% hazard multiplier)
- Driver Alert: "🚫 DANGEROUS - Hail storm with strong wind. Seek shelter immediately. This location is unsafe for delivery."

**Recommendation:**
- Skip that delivery until storm passes
- Redistribute to other vehicles/next day
- Priority scored locations get priority for reschedule

---

## 📊 Monitoring & Analytics

### Health Check Endpoint

```bash
curl -X POST http://127.0.0.1:8000/health-check \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

**Response:**
```json
{
  "status": "operational",
  "weather_api": "available",
  "routing_api": "available",
  "sample_weather": {
    "depot": {
      "rain_mm": 0,
      "wind_kmh": 15,
      "temperature_c": 28,
      "risk_level": "safe",
      "hazards": []
    },
    "hazards_detected": false
  }
}
```

---

## 🚀 Implementation Tips

### For Dispatchers

1. **Check Priority Scores First**: Sort orders by score to identify urgent deliveries
2. **Review Hazard Summary**: See at-a-glance what weather challenges each route faces
3. **Use Driver Instructions**: These are pre-built alerts you can relay to drivers via SMS/app
4. **Monitor Risk Levels**: Filter routes by risk level for operations planning

### For Drivers

1. **Read Instructions First**: Check for DANGEROUS/WARNING alerts before starting
2. **Follow Estimated Arrivals**: Account for weather delays; don't rush
3. **Check Per-Stop Alerts**: Know hazards before arriving at each location
4. **Report Conditions**: Feedback on actual vs. forecasted weather helps ML model improve

### For Operations

1. **Historical Data**: Collect delivery outcomes (spoilage, delays) + actual weather
2. **ML Improvements**: Train custom priority model with your data
3. **Risk Thresholds**: Tune hazard detection thresholds based on fleet safety record
4. **Integration**: Connect to real-time traffic/road closure APIs for future enhancements

---

## 🔮 Future Enhancements

- **Real-time Traffic Integration**: Google Maps / TomTom API
- **Road Closure API**: Integrate with govt/municipality closure notifications
- **IoT Temperature Sensors**: Monitor actual vehicle temps vs. predicted
- **Driver Feedback Loop**: Gamify route success (on-time + no spoilage = rewards)
- **ML Model Training**: XGBoost priority scoring with historical data
- **Multi-Modal Routing**: Rail/air segments for long-distance cold-chain
- **Carbon Footprint**: Minimize emissions alongside time/cost
