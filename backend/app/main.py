from fastapi import FastAPI

from app.database import Base, engine
from app.logging_config import structured_logging_middleware
from app.routers import ads, campaigns, dashboard, events, health, metrics, quality, users


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="Ad Quality Automation Platform",
        description="Testing-focused mini ad platform for delivery, tracking, attribution, and quality checks.",
        version="0.1.0",
    )
    app.middleware("http")(structured_logging_middleware)
    app.include_router(dashboard.router)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(campaigns.router)
    app.include_router(ads.router)
    app.include_router(events.router)
    app.include_router(metrics.router)
    app.include_router(quality.router)
    return app


app = create_app()
