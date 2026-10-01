import tempfile
from pathlib import Path

ENERGY_CHARTS_BASE_URL = "https://api.energy-charts.info/v2/"
BIDDING_ZONE = "DE-LU"

NEXT_DAY_PRICES_FILE = Path(tempfile.gettempdir()) / "next_day_prices.json"

HTTP_TIMEOUT_SECONDS = 60.0
HTTP_CONNECT_TIMEOUT_SECONDS = 3.0
