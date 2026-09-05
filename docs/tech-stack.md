# FarmLink Platform: Basic Tech Stack

## Frontend

- Static HTML pages for buyer, farmer/seller, driver, login, OTP, and onboarding flows.
- Vanilla JavaScript for page logic, Firebase integration, forms, and UI state.
- CSS with shared design systems, responsive layouts, Hindi-first UI, and driver-specific styles.
- Leaflet.js with OpenStreetMap tiles for interactive maps.
- Lucide icons and Google Fonts loaded from public CDNs.

## Backend and Data

- Firebase Authentication for phone/OTP sign-in.
- Cloud Firestore for users, profiles, listings, orders, deliveries, events, KYC, and payments.
- Firebase Storage for document and proof-of-delivery uploads.
- Firebase Hosting serves the static web application from `public/`.
- LocalStorage provides demo/offline fallback data for the prototype.

## Route Optimization Service

- Python 3 application in `farmlink-route-bot/`.
- FastAPI exposes `POST /optimize`, `GET /health`, and `POST /health-check`.
- Uvicorn runs the FastAPI service.
- Pydantic validates locations, orders, vehicles, weather, and road conditions.
- Google OR-Tools solves pickup-and-delivery vehicle routing.
- Optimization considers road distance/time, weather risk, load capacity, pickup order, service time, deadlines, cold-chain needs, fuel cost, tolls, closures, and route duration.
- OSRM provides road-network distance, duration, and route data.
- Open-Meteo provides weather forecasts without an API key.
- Haversine distance and neutral weather are used as fallbacks when external APIs fail.

## Supporting APIs and Tools

- OpenStreetMap Nominatim provides address geocoding for map locations.
- data.gov.in Post Office API resolves Indian PIN-code locations.
- Google Maps links provide external driver navigation.
- Python dependencies: FastAPI, Uvicorn, HTTPX, OR-Tools, Pydantic, and Pydantic Settings.

## Architecture

- Static frontend and Firebase data layer are separated from the Python route service.
- Browser pages send validated route requests to the optimizer and render the returned route, ETA, risk, cost, and logistics information.
