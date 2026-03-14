from fastapi import FastAPI, HTTPException
import random
from datetime import datetime

app = FastAPI()

# Instruments list
INSTRUMENTS = ["AAPL", "BTC-USD", "ETH-USD", "TSLA"]


def generate_market_data():

    data = []

    for instrument in INSTRUMENTS:

        record = {
            "instrument_id": instrument,
            "price": round(random.uniform(100, 50000), 2),
            "volume": round(random.uniform(1, 1000), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        data.append(record)

    return data


@app.get("/v1/market-data")
def get_market_data():

    # Fault Injection (5%)
    if random.random() < 0.05:

        # return server error
        if random.random() < 0.5:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        # malformed data
        else:
            return [{
                "instrument_id": "AAPL",
                "price": "INVALID_PRICE",
                "volume": 100,
                "timestamp": datetime.utcnow().isoformat()
            }]

    return generate_market_data()