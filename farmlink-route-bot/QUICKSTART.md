# FarmLink Route Bot v2.0 - Quick Start (5 Minutes)

## 🚀 Get Running in 5 Minutes

### Step 1: Install (2 minutes)

```powershell
# Navigate to project


# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### Step 2: Start Server (1 minute)

```powershell
uvicorn app:app --reload
```

Expected output:

```
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Test API (2 minutes)

**Option A: Interactive Docs**

- Open browser: http://127.0.0.1:8000/docs
- Scroll to "POST /optimize"
- Click "Try it out"
- Click "Execute"

**Option B: PowerShell**

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/optimize `
  -ContentType 'application/json' `
  -InFile sample_request.json | ConvertTo-Json -Depth 5
```

## 📊 Understanding the Response

The response has 4 main sections:

### 1. Routes (For Drivers)

```json
"routes": [
  {
    "vehicle_id": "truck-1",
    "overall_risk": "caution",          // 🔴 LOOK HERE: Risk level
    "driver_instructions": "...",       // 🔴 LOOK HERE: Safety guidance
    "stops": [
      {
        "stop": "Farm Name",
        "load_before_kg": 0,
        "load_after_kg": 240,
        "alert": {                      // 🔴 NEW: Weather alerts
          "severity": "caution",
          "message": "Weather alert: heavy_rain",
          "recommendation": "Monitor conditions"
        }
      }
    ]
  }
]
```

### 2. Summary (Overall Metrics)

```json
"summary": {
  "total_distance_km": 125.8,
  "weather_adjusted_minutes": 356.2,   // 🔴 Adjusted for weather!
  "served_orders": 3
}
```

### 3. Priorities (For Dispatcher)

```json
"ai_priorities": [
  {
    "order_id": "ORD-101",
    "priority_score": 85,               // 🔴 0-100 score
    "reason": "Priority: highly perishable; weather risk at pickup (caution); tight deadline",
    "pickup_risk": "caution",           // 🔴 NEW: Risk by location
    "delivery_risk": "safe"
  }
]
```

### 4. Data Sources

```json
"data_sources": {
  "routing": "osrm",                   // What routing service was used
  "weather": ["open-meteo"]            // What weather service was used
}
```

---

## 🎯 Key Features to Try

### 1. Check Health

```bash
curl http://127.0.0.1:8000/health
```

### 2. Detailed Health Check

```bash
curl -X POST http://127.0.0.1:8000/health-check \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

### 3. Full Optimization

```bash
curl -X POST http://127.0.0.1:8000/optimize \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

---

## 🔧 Customize the Sample Request

Edit `sample_request.json` to test different scenarios:

### Scenario 1: Test Weather Hazards

Modify rain amount to see alerts change:

```json
// In sample_request.json, change:
"elevation_m": 50,      // Low elevation
```

Then run - watch for "FLOODING RISK" alert at low elevation with rain.

### Scenario 2: Test Cold-Chain

Add strawberry order (needs cold storage):

```json
{
  "id": "ORD-BERRY",
  "crop": "Strawberry",
  "quantity_kg": 50,
  "perishability": 5,
  "storage_temp_c": 4,
  "promised_delivery_hours": 6
}
```

Notice: **Higher priority** than other items due to cold-chain.

### Scenario 3: Test Tight Deadline

Change promised_delivery_hours:

```json
"promised_delivery_hours": 4  // Very tight!
```

Result: **Higher priority score** due to deadline.

---

## 📖 Next: Read Documentation

Follow this order:

1. **README.md** (5 min)
   - Architecture overview
   - Feature highlights
   - What's new in v2.0

2. **FEATURES_GUIDE.md** (15 min)
   - How each feature works
   - Hazard detection explained
   - Priority scoring formula
   - Driver interface walkthrough

3. **API_REFERENCE.md** (10 min)
   - All endpoints documented
   - Request/response examples
   - Error codes
   - Performance tips

4. **DEPLOYMENT.md** (10 min)
   - Production setup
   - Docker deployment
   - Monitoring
   - Troubleshooting

---

## ⚡ Common Tasks

### Task: Change Weather API

```python
# In app.py or set environment variable:
WEATHER_API_URL=https://api.weatherapi.com/v1/forecast
```

### Task: Change Routing Service

```python
# In app.py or set environment variable:
OSRM_BASE_URL=https://your-osrm-server.com
```

### Task: Increase Time Limit

```python
# In app.py, change:
parameters.time_limit.seconds = 10  # was 5
```

### Task: Adjust Hazard Sensitivity

```python
# In app.py, in assess_weather_hazards():
if weather.rain_mm > 15:  # was 20, now more sensitive
    hazards.append(NaturalHazard.FLOODING)
```

---

## 🐛 Troubleshooting

### "Connection refused"

- Server not running? Run `uvicorn app:app --reload`
- Wrong port? Default is 8000

### "No feasible route"

- Vehicle too small? Increase capacity_kg
- Orders too large? Reduce quantity_kg
- Try with fewer orders

### "API timeout"

- Internet connection? Check connectivity
- Open-Meteo down? Check status.open-meteo.com
- Normal - it will fall back to safe defaults

### "Weather not updating"

- API unavailable? Fallback weather is used
- Check logs for HTTP errors
- Response still works, just with neutral weather

---

## 🎓 Learning Path

**Beginner** (15 min)

1. Run quickstart
2. Test sample requests
3. Read README.md

**Intermediate** (45 min)

1. Understand FEATURES_GUIDE.md
2. Modify sample_request.json
3. Try different scenarios

**Advanced** (2 hours)

1. Study API_REFERENCE.md details
2. Read deployment guide
3. Plan integration with your system

**Expert** (varies)

1. Add ML model to priority scoring
2. Integrate real-time APIs
3. Scale to production

---

## 📞 Help

**Q: What do the new fields do?**
A: See FEATURES_GUIDE.md

**Q: How do I integrate this?**
A: See API_REFERENCE.md

**Q: How do I deploy?**
A: See DEPLOYMENT.md

**Q: What went wrong?**
A: See DEPLOYMENT.md troubleshooting section

---

## 🎯 Success Checklist

- [ ] Server running locally
- [ ] API responding at http://127.0.0.1:8000/docs
- [ ] Sample request returns valid response
- [ ] Response includes weather alerts
- [ ] Priority scores make sense
- [ ] Driver instructions are clear
- [ ] You understand the new features

**All checked?** → You're ready to integrate! 🚀

---

## 🚀 Integration Steps

1. **Update your request format**
   - Add elevation_m to locations
   - Add storage_temp_c to orders
   - Add promised_delivery_hours to orders

2. **Parse new response fields**
   - Extract overall_risk from routes
   - Show driver_instructions to drivers
   - Display alerts for each stop
   - Use priority_score for dispatch

3. **Display to users**
   - Show risk level (color coding)
   - Show hazard alerts
   - Show priority scores
   - Show recommended delivery order

4. **Monitor results**
   - Track actual delivery times vs. predicted
   - Monitor weather vs. forecast accuracy
   - Collect spoilage/damage data
   - Refine hazard thresholds

---

**Version**: 2.0.0-enhanced | **Status**: ✅ Ready to Use
