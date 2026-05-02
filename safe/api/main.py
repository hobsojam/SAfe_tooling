import uvicorn
from fastapi import FastAPI

from safe.api.deps import lifespan
from safe.api.routers import (
    arts, teams, pi, iterations, features, stories,
    objectives, risks, dependencies, capacity_plans, compute,
)

app = FastAPI(
    title="SAFe Tooling API",
    version="1.0.0",
    description="HTTP API for SAFe PI Planning tooling",
    lifespan=lifespan,
)

app.include_router(arts.router)
app.include_router(teams.router)
app.include_router(pi.router)
app.include_router(iterations.router)
app.include_router(features.router)
app.include_router(stories.router)
app.include_router(objectives.router)
app.include_router(risks.router)
app.include_router(dependencies.router)
app.include_router(capacity_plans.router)
app.include_router(compute.router)


def run() -> None:
    import os
    host = os.environ.get("SAFE_API_HOST", "127.0.0.1")
    port = int(os.environ.get("SAFE_API_PORT", "8000"))
    uvicorn.run("safe.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
