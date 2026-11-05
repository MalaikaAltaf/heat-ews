from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, sites, environment, workplace, alerts, validation

app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    version=settings.VERSION,
    description="AI-Assisted Occupational Heat and Environmental Early Warning System (Abu Dhabi, UAE)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS Middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local and deployed demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(sites.router, prefix=settings.API_V1_STR)
app.include_router(environment.router, prefix=settings.API_V1_STR)
app.include_router(workplace.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(validation.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health():
    """System health endpoint (SRS OPS-01)."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "location": "Abu Dhabi, UAE",
        "timezone": settings.TIMEZONE,
        "data_provenance": {
            "environmental": "Open-Meteo Weather & Air Quality API (cached/live)",
            "workplace": "Synthetic Aggregate Shift Feeds (PRV-01 small-cell protected)",
            "clinical_disclaimer": "Prototype decision-support system. Not a validated clinical diagnostic service."
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
