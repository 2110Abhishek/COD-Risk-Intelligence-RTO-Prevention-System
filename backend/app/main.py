from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.core.database import engine, Base
from app.api.routes import (
    health,
    orders,
    decisions,
    whatsapp,
    payments,
    dashboard,
    configuration,
    analytics,
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered COD order risk assessment, decision automation, and RTO prevention platform.",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api/v1
app.include_router(health.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(decisions.router, prefix="/api/v1")
app.include_router(whatsapp.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(configuration.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to COD Risk Intelligence & RTO Prevention API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
