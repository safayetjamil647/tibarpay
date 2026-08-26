from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import hashlib
import random
import time
from app.database import engine, get_db
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tibarpay Market Service")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandleData(BaseModel):
    time: int  # Unix timestamp in seconds
    open: float
    high: float
    low: float
    close: float
    volume: float

# MARKET ROUTES
@app.get("/api/market/history", response_model=List[CandleData])
def get_market_history(symbol: str = "BTCUSD", count: int = 150, db: Session = Depends(get_db)):
    """
    Generates deterministic mock historical OHLCV data for TradingView charts
    so that each symbol has consistent charts and load states.
    """
    seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16) % 10000000
    rng = random.Random(seed)
    
    # Establish base rates and volatility
    if "BTC" in symbol:
        price = 63500.0
        volatility = 0.018
    elif "ETH" in symbol:
        price = 3450.0
        volatility = 0.022
    elif "AAPL" in symbol:
        price = 178.50
        volatility = 0.010
    elif "TSLA" in symbol:
        price = 210.20
        volatility = 0.024
    elif "MSFT" in symbol:
        price = 415.00
        volatility = 0.009
    else:
        price = 100.0
        volatility = 0.015

    end_time = int(time.time())
    candle_interval = 86400  # 1 day in seconds
    start_time = end_time - (count * candle_interval)
    
    candles = []
    current_price = price
    
    for i in range(count):
        t = start_time + (i * candle_interval)
        # Apply standard brownian motion-like steps
        change_pct = rng.normalvariate(0.0001, volatility)
        open_price = current_price
        close_price = current_price * (1 + change_pct)
        
        # Determine High / Low bounds
        high_price = max(open_price, close_price) * (1 + abs(rng.normalvariate(0, volatility * 0.4)))
        low_price = min(open_price, close_price) * (1 - abs(rng.normalvariate(0, volatility * 0.4)))
        
        volume = rng.uniform(1000, 50000)
        if "BTC" in symbol or "ETH" in symbol:
            volume = rng.uniform(100, 2500)
            
        candles.append({
            "time": t,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": round(volume, 2)
        })
        current_price = close_price
        
    return candles
