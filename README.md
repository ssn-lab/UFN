# FloodSense AI — Urban Flood Nowcasting System

> **Situational Urban Flood Risk Exploration & Nowcasting Prototype**  
> Developed for hackathon demonstration and academic situational awareness drills.

FloodSense AI combines **Open-Meteo live numerical weather forecasts**, hydrological **Rational Runoff equations ($Q = C \cdot I \cdot A$)**, municipal drainage capacity assumptions, and **crowdsourced citizen waterlogging reports** to provide high-resolution urban flood nowcasts for cities worldwide.

---

## 🌟 Key Features & Interactive Labs

1. **Global City Search & Geocoding**: Search any municipality worldwide via Open-Meteo Geocoding API, with instant preset benchmarks (Mumbai, Houston, London, Manila, Tokyo, New York).
2. **Current Weather & Ambient Telemetry**: Real-time precipitation rate (mm/h), surface temperature, relative humidity, wind speed, barometric pressure, and WMO condition decoding.
3. **3-Hour Immediate Precipitation Nowcast**: Hourly precipitation volume (mm), precipitation probability (%), WMO icon descriptions, and localized gutter inflow load.
4. **Interactive Leaflet Disaster Map**: Centered on the selected city with CartoDB Dark Matter tiles, simulated micro-catchment vulnerability polygons (colored by risk), and citizen waterlogging incident pins.
5. **Flood Risk Categorization Engine**: Clear categorization into **LOW**, **MODERATE**, **HIGH**, and **VERY HIGH** risk tiers with composite 0-100 scoring and dominant factor identification.
6. **24-Hour Rainfall & Risk Trajectory Charts**: Recharts composed bar and line charts showing precipitation vs municipal drainage threshold and changing risk score over time.
7. **The "Duck-O-Meter" Flood Depth Gauge 🦆**: An interactive visual street cross-section translating centimeters of urban water accumulation into real-world consequences (Rubber Duck floating, soggy socks, car exhaust submergence, kayaking zone, to submarine clearance).
8. **"Can I Drive Through It?" Vehicle Wading Evaluator 🚗**: An interactive simulator calculating air-intake and hydrolock limits for Electric Scooters, Bicycles, Sedans, SUVs, and 4x4 Off-Roaders against current water depths with humorous safety reality checks.
9. **"Drainage Tycoon" $10M Infrastructure Sandbox 🚇**: A municipal budget simulator where users allocate $10M across deep discharge vaults, sponge pavements, and bioswales to engineer resilience and drop the flood risk score in real time.
10. **Commuter Flood Survival Index & Readiness Kit 🎒**: Interactive checklist testing personal flash-flood readiness (waterproof boots, dry phone pouches, offline maps, and pool floats) with a dynamic rank score.
11. **Atmospheric Canvas Rain Drops & Web Audio Synthesizer 🌧️🔊**: Procedural rain sound generator and animated canvas raindrops overlay that automatically scales with live city rainfall rates.
12. **Drainage-Risk Stress-Test Simulator**: Interactive sliders for rainfall intensity, storm drain capacity, concrete imperviousness %, antecedent soil saturation, and storm duration with dynamic hydrograph and civil engineering mitigation tips.
13. **Citizen Waterlogging Center**: Community reporting system where users can submit waterlogging observations (ankle, knee, waist, submerged) with instant map pin updates.
14. **Transparent Disclaimers & Integrity Labels**:
    - Live Open-Meteo API data labeled with timestamps.
    - Synthetic micro-catchment zones labeled as `SIMULATED CATCHMENT`.
    - Clear disclaimers stating that risk outputs are computational estimates, not civil emergency warnings.
15. **Offline Resilience & Demo Mode**: One-click switch to deterministic scenario profiles if external APIs are unreachable or offline.

---

## 🏗️ Architecture & Tech Stack

```
floodsense-ai/
├── backend/
│   ├── config.py                 # Environment variables and CORS configuration
│   ├── main.py                   # FastAPI server & route handlers
│   ├── requirements.txt          # Python dependencies (FastAPI, Uvicorn, HTTPX, Pytest)
│   ├── data/
│   │   └── reports.json          # Citizen reports persistence store
│   ├── services/
│   │   ├── flood_model.py        # Hydrological nowcasting & Rational Method formulas
│   │   ├── open_meteo.py         # Open-Meteo Forecast & Geocoding client + offline fallback
│   │   ├── storage.py            # Local report storage with initial benchmark seed
│   │   └── hotspots.py           # Synthetic micro-catchment polygon generator
│   └── tests/
│       ├── test_flood_model.py   # Unit tests for hydrological calculations
│       └── test_api.py           # Integration tests for FastAPI endpoints
│
└── frontend/
    ├── package.json              # React 19, Vite, Leaflet, React-Leaflet, Recharts, Lucide
    ├── vite.config.js            # Vite configuration with /api backend proxy
    ├── index.html                # Entry HTML with disaster-management typography & Leaflet styles
    └── src/
        ├── index.css             # Dark navy disaster-management design system
        ├── App.jsx               # Root application component
        ├── utils/
        │   └── audio.js          # Procedural Web Audio API rain & click synthesizer
        ├── services/
        │   └── api.js            # Frontend API client
        └── components/
            ├── Header.jsx        # Search, presets, audio & rain canvas controls
            ├── Sidebar.jsx       # Operations navigation & interactive labs
            ├── NowcastMetrics.jsx# Risk tier, precipitation, ambient telemetry, drainage deficit
            ├── NowcastCards.jsx  # Next 3 hours precipitation breakdown cards
            ├── FloodMap.jsx      # Leaflet map with simulated hotspots & report markers
            ├── RainfallChart.jsx # 24h precipitation & risk trajectory charts
            ├── DuckOMeter.jsx    # Interactive "Duck-O-Meter" depth cross-section
            ├── VehicleWadingEvaluator.jsx # "Can I Drive Through It?" wading tool
            ├── DrainageTycoon.jsx# $10M urban infrastructure investment simulator
            ├── SurvivalChecklist.jsx # Commuter survival readiness checklist
            ├── RainCanvas.jsx    # Interactive atmospheric canvas rain overlay
            ├── DrainageSimulator.jsx # Urban drainage sandbox & hydrograph
            ├── CitizenReportsView.jsx # Ground observations feed & filters
            ├── CitizenReportModal.jsx # Waterlog incident submission modal
            └── SystemDisclaimers.jsx  # Transparency disclosures & formulas
```

---

## 🚀 Windows Setup & Launch Instructions

### Prerequisites
- **Python 3.10+** (verified on Python 3.12)
- **Node.js 18+** and **npm**

> **Note for Windows PowerShell users**: When running npm or npx commands in PowerShell, always use `npm.cmd` and `npx.cmd` to bypass PowerShell script execution restrictions.

---

### 1. Backend Setup & Startup

Open a PowerShell terminal:

```powershell
# Navigate to the backend directory
cd C:\Users\ravin\.gemini\antigravity-ide\scratch\floodsense-ai\backend

# Create a virtual environment (if not already created)
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
# (Or run directly via .\venv\Scripts\python.exe)

# Install dependencies
.\venv\Scripts\pip.exe install -r requirements.txt

# Run backend tests to verify calculations
.\venv\Scripts\pytest.exe .\tests -v

# Start the FastAPI server on port 8000
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:
- **API URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

---

### 2. Frontend Setup & Startup

Open a second PowerShell terminal:

```powershell
# Navigate to the frontend directory
cd C:\Users\ravin\.gemini\antigravity-ide\scratch\floodsense-ai\frontend

# Install dependencies
npm.cmd install

# Start the Vite development server on port 5173
npm.cmd run dev
```

The frontend application will be live at:
- **Dashboard URL**: `http://localhost:5173`

---

## 🧪 Testing

Run the automated test suite covering hydrological calculations and API endpoints:

```powershell
cd C:\Users\ravin\.gemini\antigravity-ide\scratch\floodsense-ai
.\backend\venv\Scripts\pytest.exe .\backend\tests -v
```

11/11 tests validate:
- Runoff coefficient bounds ($C$ between 0.15 and 0.96)
- Drainage exceedance thresholds and time-to-ankle-depth calculations
- Nowcast risk categorization (LOW, MODERATE, HIGH, VERY HIGH)
- Health, geocoding search, deterministic nowcast, simulation, and citizen report submission endpoints.

---

## ⚖️ Scientific Assumptions & Disclaimers

1. **Heuristic Nature**: Outputs represent predictive hydrological heuristics based on the Rational Method. They do not constitute official emergency evacuation orders.
2. **Drainage Infrastructure**: Municipal drainage capacity is parameterized as a generalized municipal metric (default 22 mm/hr). The prototype does not map physical subterranean conduit dimensions.
3. **Simulated Features**: Micro-catchment hotspots and baseline incidents are synthetically parameterized for scenario evaluation.
4. **Data Attribution**: Real-time meteorological data is provided by [Open-Meteo](https://open-meteo.com/) under open data terms. Map basemaps are provided by [CartoDB](https://carto.com/) and [OpenStreetMap](https://www.openstreetmap.org/).
