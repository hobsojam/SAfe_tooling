import uvicorn
from fastapi import FastAPI

from safe.api.deps import lifespan

app = FastAPI(
    title="SAFe Tooling API",
    version="1.0.0",
    description="HTTP API for SAFe PI Planning tooling",
    lifespan=lifespan,
)


def run() -> None:
    import os
    host = os.environ.get("SAFE_API_HOST", "127.0.0.1")
    port = int(os.environ.get("SAFE_API_PORT", "8000"))
    uvicorn.run("safe.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
