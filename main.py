from fastapi import FastAPI, Request, HTTPException
from pydantic import HttpUrl
from httpx import AsyncClient, Timeout
import json
import tempfile
from pathlib import Path
import asyncio

from contextlib import asynccontextmanager

NEXT_DAY_PRICES_FILE = Path(tempfile.gettempdir()) / "next_day_prices.json"

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncClient(
        base_url="https://api.energy-charts.info/v2",
        timeout=Timeout(60.0, connect=3.0)
    )as client:
        app.state.external_api = client
        yield

app = FastAPI(lifespan=lifespan)

def save_prices(data):
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=NEXT_DAY_PRICES_FILE.parent,
        delete=False,
    ) as file:
        json.dump(data, file)
        temporary_path = Path(file.name)

    temporary_path.replace(NEXT_DAY_PRICES_FILE)

def process_prices(data):
    data = json.loads(data)

    price_list = data["data"]
    price_average_every_3_hours = []

    print(price_list)

    for i in range(len(price_list) - 11):
        interval_price_sum = 0

        for j in range(12):
            interval_price_sum += price_list[i + j]["values"]["day_ahead_price"]

        starting_hour = price_list[i]["timestamp"]
        ending_hour = price_list[i + 11]["timestamp"]
        average_price = interval_price_sum / 12

        price_average_every_3_hours.append({
            "starting_hour": starting_hour,
            "ending_hour": ending_hour,
            "average_price": average_price
        })
       
    return price_average_every_3_hours

@app.get("/prices_next_day")
async def get_prices_next_day(request: Request):
    client: AsyncClient = request.app.state.external_api

    try:
        response = await client.get("/price", params={"bzn": "DE-LU"})
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    await asyncio.to_thread(save_prices, data)

    return data

@app.get("/lowest_price_interval")
async def get_lowest_price_interval():

    try:
        content = await asyncio.to_thread(NEXT_DAY_PRICES_FILE.read_text, encoding="utf-8")

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price data not found. Please fetch the prices first.")

    processed_data = process_prices(content)
    lowest_price_interval = min(processed_data, key=lambda x: x["average_price"])

    return lowest_price_interval

@app.get("/highest_price_interval")
async def get_highest_price_interval():

    try:
        content = await asyncio.to_thread(NEXT_DAY_PRICES_FILE.read_text, encoding="utf-8")

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price data not found. Please fetch the prices first.")

    processed_data = process_prices(content)
    highest_price_interval = max(processed_data, key=lambda x: x["average_price"])

    return highest_price_interval

