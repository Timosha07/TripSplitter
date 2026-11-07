import asyncio
from decimal import Decimal
import time
import yfinance as yf

_cache = {}
_lock = asyncio.Lock()

def _fetch(code):
    data = yf.Ticker(f"{code}KZT=X").history(period="5d", timeout=8)
    if data.empty:
        raise ValueError("No exchange rate")
    rate = Decimal(str(data['Close'].iloc[-1]))
    if not rate.is_finite() or rate <= 0:
        raise ValueError("Invalid exchange rate")
    return rate

async def get_exchange_rate(code):
    if code == 'KZT':
        return Decimal(1)
    async with _lock:
        cached = _cache.get(code)
        if cached and time.monotonic() - cached[0] < 3600:
            return cached[1]
        rate = await asyncio.wait_for(asyncio.to_thread(_fetch, code), timeout=12)
        _cache[code] = (time.monotonic(), rate)
        return rate
