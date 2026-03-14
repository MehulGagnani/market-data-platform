```python
import requests
import statistics
import time
import psycopg2
from models import MarketData

API_URL = "http://api:8000/v1/market-data"

# Database connection
conn = psycopg2.connect(
    host="db",
    database="market",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()


# Extract
def fetch_data():

    try:
        response = requests.get(API_URL, timeout=5)

        if response.status_code != 200:
            print("API error:", response.status_code)
            return []

        return response.json()

    except Exception as e:
        print("Request failed:", e)
        return []


# Schema Validation
def validate_data(records):

    valid_records = []
    dropped = 0

    for record in records:

        try:
            data = MarketData(**record)
            valid_records.append(data)

        except Exception:
            dropped += 1

    return valid_records, dropped


# Outlier Detection
def detect_outliers(data):

    prices = {}

    for record in data:
        prices.setdefault(record.instrument_id, []).append(record.price)

    avg_prices = {
        instrument: statistics.mean(values)
        for instrument, values in prices.items()
    }

    flagged = []

    for record in data:

        avg = avg_prices[record.instrument_id]

        if abs(record.price - avg) / avg > 0.15:
            flagged.append(True)
        else:
            flagged.append(False)

    return flagged


# VWAP Calculation
def calculate_vwap(data):

    result = {}

    for record in data:

        if record.instrument_id not in result:
            result[record.instrument_id] = {"pv": 0, "v": 0}

        result[record.instrument_id]["pv"] += record.price * record.volume
        result[record.instrument_id]["v"] += record.volume

    return {
        k: v["pv"] / v["v"]
        for k, v in result.items()
    }


# Load to Postgres
def insert_into_db(data):

    for record in data:

        cursor.execute(
            """
            INSERT INTO market_data (symbol, price, volume)
            VALUES (%s, %s, %s)
            """,
            (record.instrument_id, record.price, record.volume)
        )

    conn.commit()


# Pipeline Runner
def run_pipeline():

    records = fetch_data()

    if not records:
        return

    valid, dropped = validate_data(records)

    outliers = detect_outliers(valid)

    vwap = calculate_vwap(valid)

    # Load step (NEW)
    insert_into_db(valid)

    print("Records Processed:", len(valid))
    print("Records Dropped:", dropped)
    print("VWAP:", vwap)
    print("Outliers:", outliers)


while True:

    run_pipeline()

    time.sleep(5)
```
