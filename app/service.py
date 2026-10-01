def process_prices(data: dict) -> list[dict]:
    price_list = data["data"]
    price_average_every_3_hours = []

    for i in range(len(price_list) - 11):
        interval_price_sum = 0

        for j in range(12):
            interval_price_sum += price_list[i + j]["values"]["day_ahead_price"]

        starting_hour = price_list[i]["timestamp"]
        ending_hour = price_list[i + 11]["timestamp"]
        average_price = interval_price_sum / 12

        price_average_every_3_hours.append(
            {
                "starting_hour": starting_hour,
                "ending_hour": ending_hour,
                "average_price": average_price,
            }
        )

    return price_average_every_3_hours


def classify_price_intervals(
    intervals: list[dict],
    data: dict,
) -> list[dict]:
    # Classify intervals based on daily average price
    # if the average price is below the daily average - threshold , classify as "low", if it's above the daily average + threshold, classify as "high", otherwise classify as "ok"
    # the threshold is 10% of the daily average price

    threshold_percentage = 0.1

    daily_prices = [record["values"]["day_ahead_price"] for record in data["data"]]

    daily_average_price = sum(daily_prices) / len(daily_prices)
    threshold = abs(daily_average_price) * threshold_percentage

    for interval in intervals:
        if interval["average_price"] < daily_average_price - threshold:
            interval["classification"] = "low"
        elif interval["average_price"] > daily_average_price + threshold:
            interval["classification"] = "high"
        else:
            interval["classification"] = "ok"

    return intervals
