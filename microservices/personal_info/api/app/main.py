from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import get_db

app = FastAPI(title="Job Hunting AI", version="1.0.0")


@app.get("/health")
async def healthcheck(db: AsyncSession = Depends(get_db)) -> dict[str, str]:

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
