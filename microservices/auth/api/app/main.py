from fastapi import FastAPI

from app.api import routers

app = FastAPI(title="Auth microservice", version="1.0.0")

for router in routers:
    app.include_router(router)

@app.get("/health")
async def healthcheck() -> dict[str, str]:

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
