# End-to-End Data Engineering Challenge


## Overview

This project demonstrates an end-to-end data pipeline that simulates real-time financial market data and processes it using an ETL pipeline before storing it in PostgreSQL.

The system is fully containerized using Docker and orchestrated with Docker Compose.

Architecture:

Mock API (FastAPI) → ETL Pipeline (Python) → PostgreSQL Database

---

## System Components

### 1. Mock API (FastAPI)

The API simulates a real-time financial data feed.

Endpoint:

GET /v1/market-data

Example response:

[
{
"instrument_id": "AAPL",
"price": 182.45,
"volume": 450,
"timestamp": "2026-03-14T14:00:10"
}
]

Chaos Engineering:

* 5% of requests intentionally fail
* Returns either:

  * HTTP 500 error
  * malformed data (invalid price type)

This helps test ETL resilience.

---

### 2. ETL Pipeline

The ETL service performs the following steps:

Extraction

* Polls the API periodically
* Handles timeouts and faulty responses

Transformation

* Schema validation using Pydantic
* VWAP (Volume Weighted Average Price) calculation
* Outlier detection (price deviation > 15%)

Quality Control

* Invalid records are dropped
* Duplicate records avoided using database constraints
* Logs report:

  * records processed
  * records dropped
  * execution time

---

### 3. Database (PostgreSQL)

Processed data is stored in PostgreSQL.

Table structure:

instrument_id | price | volume | timestamp

Primary key:

(instrument_id, timestamp)

This ensures idempotency and prevents duplicate records.

---

## Infrastructure (Docker)

The system runs using three containers:

1. API container (FastAPI)
2. ETL container (Python pipeline)
3. PostgreSQL container

All services communicate using Docker's internal network.

---

## Running the Project

Requirements:

* Docker
* Docker Compose

* Clone the repository:

git clone https://github.com/MehulGagnani/market-data-platform.git
cd market-data-platform


Run the entire system:

docker compose up --build

This will start:

* API server
* ETL pipeline
* PostgreSQL database

Test API:

http://localhost:8000/v1/market-data

---

# System Design Questions

## 1. Scaling to 1 Billion Events per Day

To scale the architecture:

API → Kafka → Stream Processing → Data Lake/Warehouse

Technologies:

* Kafka for high-throughput event streaming
* Spark Structured Streaming or Flink for distributed processing
* Object storage (S3 / Data Lake)
* Data warehouse (Snowflake / BigQuery / Redshift)

Benefits:

* horizontal scalability
* fault tolerance
* real-time processing

---

## 2. Monitoring and Health Checks

Production monitoring can be implemented using:

Health Checks

* API `/health` endpoint
* ETL heartbeat logs

Monitoring stack:

* Prometheus (metrics collection)
* Grafana (visual dashboards)
* ELK stack for log monitoring

Key metrics:

* API latency
* records processed
* error rate
* ETL execution time

---

## 3. Idempotency and Recovery

To ensure safe recovery and prevent duplicates:

1. Database constraints

Primary key:

(instrument_id, timestamp)

2. Upsert logic

INSERT ... ON CONFLICT DO NOTHING

3. Checkpointing

The ETL pipeline can store the last processed timestamp and resume processing from that point.

4. Retry strategy

Failed API calls are retried with exponential backoff.

---

## Conclusion

This project demonstrates an end-to-end data engineering workflow including:

* API data ingestion
* schema validation
* data transformation
* database storage
* containerized deployment

The system is designed to be scalable, resilient, and portable.
