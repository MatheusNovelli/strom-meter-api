import asyncio
import json
import tempfile
from pathlib import Path

from app.config import NEXT_DAY_PRICES_FILE


def _write_prices(data: dict) -> None:
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=NEXT_DAY_PRICES_FILE.parent,
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(data, file)

        temporary_path.replace(NEXT_DAY_PRICES_FILE)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _read_prices() -> dict:
    content = NEXT_DAY_PRICES_FILE.read_text(encoding="utf-8")
    return json.loads(content)


async def save_prices(data: dict) -> None:
    await asyncio.to_thread(_write_prices, data)


async def load_prices() -> dict:
    return await asyncio.to_thread(_read_prices)
