from fastapi import FastAPI

from app.routes.exercises import router as exercises_router
from app.routes.health import router as health_router
from app.routes.workouts import router as workouts_router


def create_app() -> FastAPI:
    app = FastAPI(title="Training App API", version="0.1.0")
    app.include_router(health_router)
    app.include_router(exercises_router)
    app.include_router(workouts_router)
    return app


app = create_app()
