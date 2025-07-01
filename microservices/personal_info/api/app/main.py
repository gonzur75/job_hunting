from fastapi import FastAPI

app = FastAPI(title="Job Hunting AI", version="1.0.0")


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
