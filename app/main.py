from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient, Timeout

from app import config
from app.router import router as prices_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncClient(
        base_url=config.ENERGY_CHARTS_BASE_URL,
        timeout=Timeout(
            config.HTTP_TIMEOUT_SECONDS,
            connect=config.HTTP_CONNECT_TIMEOUT_SECONDS,
        ),
    ) as client:
        app.state.external_api = client
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(prices_router)
