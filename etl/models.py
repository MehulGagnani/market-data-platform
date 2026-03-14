from pydantic import BaseModel
from datetime import datetime

class MarketData(BaseModel):

    instrument_id: str
    price: float
    volume: float
    timestamp: datetime