from httpx import AsyncClient

from app.config import BIDDING_ZONE


async def fetch_next_day_prices(client: AsyncClient) -> dict:
    response = await client.get(
        "price_next_day",
        params={"bzn": BIDDING_ZONE},
    )
    response.raise_for_status()
    return response.json()
