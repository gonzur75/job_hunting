from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import get_db
from .api import routers

app = FastAPI(title="Job Hunting AI", version="1.0.0")

for router in routers:
    app.include_router(router)

@app.get("/health")
async def healthcheck(db: AsyncSession = Depends(get_db)) -> dict[str, str]:

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
