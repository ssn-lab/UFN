"""
FloodSense AI — Urban Flood Nowcasting System Backend
FastAPI server exposing hydrological nowcasting, weather integration,
drainage simulation, and citizen waterlogging reporting APIs.
"""

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from config import settings
from services.open_meteo import OpenMeteoService, DEMO_CITIES
from services.flood_model import FloodRiskModel
from services.storage import ReportStorage
from services.hotspots import HotspotService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Situational urban flood risk nowcasting prototype powered by Open-Meteo forecasts and hydrological drainage modeling."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Pydantic Models -----------------

class DrainageSimulationRequest(BaseModel):
    rainfall_rate_mm_hr: float = Field(..., ge=0.0, le=250.0, description="Rainfall intensity in mm/hour")
    drainage_capacity_mm_hr: float = Field(default=22.0, ge=5.0, le=100.0, description="Stormwater drainage capacity in mm/hour")
    impervious_surface_pct: float = Field(default=70.0, ge=0.0, le=100.0, description="Percentage of concrete/asphalt pavement")
    soil_saturation_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Soil moisture saturation %")
    storm_duration_hours: float = Field(default=3.0, ge=0.5, le=12.0, description="Duration of continuous precipitation event")

class CitizenReportCreate(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_name: str = Field(..., min_length=2, max_length=200)
    water_depth: str = Field(..., min_length=2, max_length=50)
    depth_level: str = Field(default="knee", pattern="^(ankle|knee|waist|submerged)$")
    description: str = Field(..., min_length=3, max_length=500)
    category: str = Field(default="Road Inundation", max_length=100)

# ----------------- Endpoints -----------------

@app.get("/api/health")
async def health_check():
    """System health check and runtime status."""
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "open_meteo_endpoint": settings.OPEN_METEO_FORECAST_URL,
        "demo_cities_count": len(DEMO_CITIES)
    }

@app.get("/api/cities/search")
async def search_cities(query: str = Query("", min_length=0, max_length=100)):
    """Search cities worldwide via Open-Meteo Geocoding API with fallback."""
    results = await OpenMeteoService.search_cities(query)
    return {
        "query": query,
        "count": len(results),
        "results": results
    }

@app.get("/api/cities/presets")
async def get_city_presets():
    """Retrieve predefined hackathon demonstration cities with varying flood risks."""
    return {
        "presets": DEMO_CITIES
    }

@app.get("/api/weather/nowcast")
async def get_nowcast(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    city_name: str = Query("Selected City"),
    drainage_capacity_mm_hr: float = Query(22.0, ge=5.0, le=100.0),
    impervious_surface_pct: float = Query(70.0, ge=0.0, le=100.0),
    force_demo: bool = Query(False)
):
    """
    Primary nowcasting endpoint.
    Retrieves weather forecast, parses the next 3h nowcast window and 24h trajectory,
    evaluates hydrological risk, and generates synthetic city catchment hotspots.
    """
    weather_data = await OpenMeteoService.get_forecast(
        latitude=latitude,
        longitude=longitude,
        city_name=city_name,
        force_demo=force_demo
    )
    
    nowcast_3h = weather_data.get("nowcast_3h", [])
    current_weather = weather_data.get("current_weather", {})
    
    current_rain = float(current_weather.get("precipitation_mm", 0.0))
    next_3h_rain = [float(h.get("precipitation_mm", 0.0)) for h in nowcast_3h]
    precip_probs = [int(h.get("precipitation_probability", 50)) for h in nowcast_3h]
    soil_saturation = float(weather_data.get("soil_saturation_pct", 50.0))

    # Evaluate hydrological risk
    risk_assessment = FloodRiskModel.evaluate_nowcast_risk(
        current_rain_mm=current_rain,
        next_3h_rain=next_3h_rain,
        precip_probabilities=precip_probs,
        soil_saturation_pct=soil_saturation,
        drainage_capacity_mm_hr=drainage_capacity_mm_hr,
        impervious_pct=impervious_surface_pct
    )

    # Generate micro-catchment hotspots for the map
    hotspots = HotspotService.get_city_hotspots(
        lat=latitude,
        lon=longitude,
        city_name=city_name,
        current_risk_score=risk_assessment["risk_score"]
    )

    # Get local citizen reports
    reports = ReportStorage.get_all(city=city_name)

    return {
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": weather_data.get("timestamp"),
        "is_live_data": weather_data.get("is_live_data", False),
        "data_source": weather_data.get("data_source"),
        "current_weather": current_weather,
        "nowcast_3h": nowcast_3h,
        "forecast_24h": weather_data.get("forecast_24h", []),
        "risk_assessment": risk_assessment,
        "hotspots": hotspots,
        "reports_count": len(reports),
        "reports": reports[:10]
    }

@app.post("/api/risk/simulate")
async def simulate_drainage_risk(req: DrainageSimulationRequest):
    """
    Interactive drainage-risk simulator.
    Evaluates net surface water inundation rate, excess water, and time to waterlogging.
    """
    runoff_c = FloodRiskModel.calculate_runoff_coefficient(
        impervious_pct=req.impervious_surface_pct,
        soil_saturation_pct=req.soil_saturation_pct
    )

    exceedance = FloodRiskModel.calculate_drainage_exceedance(
        rainfall_rate_mm_hr=req.rainfall_rate_mm_hr,
        drainage_capacity_mm_hr=req.drainage_capacity_mm_hr,
        runoff_coeff=runoff_c
    )

    # Calculate hourly accumulation timeline across storm duration
    accumulation_timeline = []
    current_water_mm = 0.0
    time_steps = int(req.storm_duration_hours * 2) # Every 30 minutes
    
    for step in range(time_steps + 1):
        elapsed_hours = step * 0.5
        inflow = req.rainfall_rate_mm_hr * runoff_c * 0.5
        drain_removal = req.drainage_capacity_mm_hr * 0.5
        net_change = inflow - drain_removal
        
        current_water_mm = max(0.0, current_water_mm + net_change)
        
        accumulation_timeline.append({
            "elapsed_hours": elapsed_hours,
            "accumulated_water_mm": round(current_water_mm, 1),
            "drain_capacity_line_mm": round(req.drainage_capacity_mm_hr * elapsed_hours, 1),
            "cumulative_rainfall_mm": round(req.rainfall_rate_mm_hr * elapsed_hours, 1),
            "status": "Inundation" if current_water_mm > 40.0 else ("Ponding" if current_water_mm > 15.0 else "Drained")
        })

    # Compute risk score for simulated parameters
    h_arr = [req.rainfall_rate_mm_hr] * 3
    sim_risk = FloodRiskModel.evaluate_nowcast_risk(
        current_rain_mm=req.rainfall_rate_mm_hr,
        next_3h_rain=h_arr,
        precip_probabilities=[100, 100, 100],
        soil_saturation_pct=req.soil_saturation_pct,
        drainage_capacity_mm_hr=req.drainage_capacity_mm_hr,
        impervious_pct=req.impervious_surface_pct
    )

    # Mitigation recommendations based on simulation
    mitigation_tips = []
    if req.impervious_surface_pct > 75.0:
        mitigation_tips.append("Permeable Pavement Conversion: Replacing 25% of asphalt could reduce runoff by up to 22%.")
    if exceedance["is_exceeded"]:
        needed_capacity = round(exceedance["effective_inflow_mm_hr"], 1)
        mitigation_tips.append(f"Storm Drain Upsizing: Drainage capacity must increase to at least {needed_capacity} mm/hr to prevent surface accumulation.")
        mitigation_tips.append("Bioswale & Retention Basin: Installing bioswales can temporarily buffer the excess runoff volume.")
    else:
        mitigation_tips.append("Current drainage infrastructure is capable of handling the simulated rainfall intensity.")

    return {
        "simulation_inputs": req.model_dump(),
        "runoff_coefficient": runoff_c,
        "effective_inflow_mm_hr": exceedance["effective_inflow_mm_hr"],
        "excess_water_mm_hr": exceedance["excess_water_mm_hr"],
        "drainage_utilization_pct": exceedance["drainage_utilization_pct"],
        "is_exceeded": exceedance["is_exceeded"],
        "minutes_to_ankle_depth": exceedance["minutes_to_ankle_depth"],
        "minutes_to_knee_depth": exceedance["minutes_to_knee_depth"],
        "simulated_risk_score": sim_risk["risk_score"],
        "simulated_risk_category": sim_risk["risk_category"],
        "severity_color": sim_risk["severity_color"],
        "timeline": accumulation_timeline,
        "mitigation_recommendations": mitigation_tips,
        "disclaimer": "Simulated hydrological estimation based on Rational Runoff formula. Intended for scenario testing."
    }

@app.get("/api/reports")
async def get_citizen_reports(city: Optional[str] = Query(None)):
    """Retrieve citizen waterlogging reports filtered by city."""
    reports = ReportStorage.get_all(city=city)
    return {
        "count": len(reports),
        "city_filter": city,
        "reports": reports
    }

@app.post("/api/reports", status_code=status.HTTP_201_CREATED)
async def submit_citizen_report(report: CitizenReportCreate):
    """Submit a local citizen waterlogging report."""
    created = ReportStorage.add_report(
        city=report.city,
        latitude=report.latitude,
        longitude=report.longitude,
        location_name=report.location_name,
        water_depth=report.water_depth,
        depth_level=report.depth_level,
        description=report.description,
        category=report.category
    )
    return {
        "message": "Waterlogging report submitted successfully. Thank you for contributing to community safety awareness.",
        "report": created
    }

@app.get("/api/hotspots")
async def get_city_hotspots(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    city_name: str = Query("Target City"),
    risk_score: float = Query(40.0, ge=0.0, le=100.0)
):
    """Retrieve micro-catchment hotspots and flood hazard zones for a city."""
    hotspots = HotspotService.get_city_hotspots(
        lat=latitude,
        lon=longitude,
        city_name=city_name,
        current_risk_score=risk_score
    )
    return {
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "count": len(hotspots),
        "hotspots": hotspots,
        "notice": "All hotspots are simulated geographic models representing theoretical micro-catchment behavior."
    }

@app.get("/api/system/limitations")
async def get_limitations():
    """Transparent disclosure of model limitations, data sources, and prototype boundaries."""
    return {
        "prototype_version": settings.VERSION,
        "data_sources": [
            {
                "name": "Open-Meteo Weather Forecast API",
                "role": "Live hourly precipitation, probability, surface temperature, humidity, and soil moisture",
                "license": "Non-commercial free tier / Open Data",
                "latency": "Hourly reanalysis and 15-minute nowcasting model updates"
            },
            {
                "name": "Open-Meteo Geocoding API",
                "role": "Global city and municipality search coordinates",
                "license": "Open-Meteo / GeoNames database"
            },
            {
                "name": "OpenStreetMap & CartoDB",
                "role": "Interactive basemap rendering",
                "license": "Open Database License (ODbL)"
            }
        ],
        "hydrological_assumptions": [
            "Runoff calculation uses modified Rational Method (Q = C * I * A) with dynamic saturation-adjusted C coefficient.",
            "Municipal drainage capacity is configured as a generalized municipal metric (default 22 mm/hr) and does not map individual subterranean pipe diameters.",
            "Micro-catchment vulnerability zones and hotspot polygons are simulated topographic approximations for demonstration and situational drill purposes.",
            "Citizen reports are community-submitted and require municipal verification before civil emergency action."
        ],
        "strict_disclaimers": [
            "FloodSense AI is an academic hackathon proof-of-concept for situational exploratory nowcasting.",
            "Calculated risk categories (LOW, MODERATE, HIGH, VERY HIGH) are computational estimates, not official civil defense warnings.",
            "Never ignore directives from local municipal disaster management authorities or emergency services."
        ]
    }
