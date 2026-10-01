import json
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app import client, service, storage

router = APIRouter(tags=["prices"])


async def load_intervals() -> list[dict]:
    try:
        data = await storage.load_prices()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Price data not found. Please fetch the prices first.",
        ) from exc

    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not read saved price data.",
        ) from exc

    intervals = service.process_prices(data)

    if not intervals:
        raise HTTPException(
            status_code=503,
            detail="Not enough price data to calculate an interval.",
        )

    return intervals


IntervalsDep = Annotated[list[dict], Depends(load_intervals)]


@router.get("/prices_next_day")
async def get_prices_next_day(request: Request):
    try:
        data = await client.fetch_next_day_prices(request.app.state.external_api)

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Price API timed out.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Tomorrow's prices are not available yet.",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Price API returned an error.",
        ) from exc

    except (httpx.RequestError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve valid price data.",
        ) from exc

    try:
        await storage.save_prices(data)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not save price data.",
        ) from exc

    return data


@router.get("/lowest_price_interval")
async def get_lowest_price_interval(intervals: IntervalsDep):
    return min(intervals, key=lambda item: item["average_price"])


@router.get("/highest_price_interval")
async def get_highest_price_interval(intervals: IntervalsDep):
    return max(intervals, key=lambda item: item["average_price"])


@router.get("/classified_price_intervals")
async def get_classified_price_intervals(intervals: IntervalsDep):
    classified_intervals = service.classify_price_intervals(
        intervals, data=await storage.load_prices()
    )
    return classified_intervals


@router.get("/price_intervals_summary")
async def get_price_intervals_summary(intervals: IntervalsDep):
    lowest_interval = min(intervals, key=lambda item: item["average_price"])
    highest_interval = max(intervals, key=lambda item: item["average_price"])
    classified_intervals = service.classify_price_intervals(
        intervals, data=await storage.load_prices()
    )

    return {
        "lowest_price_interval": lowest_interval,
        "highest_price_interval": highest_interval,
        "classified_price_intervals": classified_intervals,
    }
