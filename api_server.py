"""
Next.js API Integration - REST API Server
Bisa dijalankan secara independen dan dipanggil dari Next.js frontend

Usage:
    npm install axios
    // Di Next.js:
    const res = await fetch('http://localhost:8000/api/bi?ticker=AAPL')
    const data = await res.json()
"""

import re
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, List, Any, Annotated
import uvicorn
import json
import sys
import os


from bi_engine import BIEngine, CacheManager, StockDataCollector, NewsScraper

# ==================== PYDANTIC MODELS ====================

class StockDataQuery(BaseModel):
    """Model untuk query parameter stock data"""
    ticker: str = Field(..., min_length=1, max_length=10)
    days: Annotated[int, Field(ge=1, le=30)] = 7


class NewsQuery(BaseModel):
    """Model untuk query parameter berita"""
    source: Optional[str] = Field("cnbc", description="News source")


class BatchQuery(BaseModel):
    """Model untuk batch analysis"""
    tickers: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of ticker symbols"
    )

    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """Validasi semua ticker"""
        validated = []
        for ticker in v:
            if not re.match(r'^[A-Z0-9.\-]+$', ticker.upper()):
                raise ValueError(f'Invalid ticker: {ticker}')
            validated.append(ticker.upper())
        return validated


class GraphQLQuery(BaseModel):
    """Model untuk GraphQL-style query"""
    ticker: str = Field(..., min_length=1, max_length=10)
    fields: List[str] = Field(
        default=["sentiment", "recommendations"],
        description="Fields to return"
    )

    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v: List[str]) -> List[str]:
        """Validasi field yang diminta"""
        valid_fields = {
            "stock_data",
            "news_data",
            "sentiment",
            "recommendations",
            "analysis"
        }
        for field in v:
            if field not in valid_fields:
                raise ValueError(f'Invalid field: {field}. Valid: {valid_fields}')
        return v


# Response models
class StockResponse(BaseModel):
    """Response model untuk stock data"""
    success: bool
    ticker: str
    data: Optional[dict] = None
    error: Optional[str] = None


class NewsResponse(BaseModel):
    """Response model untuk news data"""
    success: bool
    source: str
    data: Optional[dict] = None
    error: Optional[str] = None


class BIResponse(BaseModel):
    """Response model untuk analisis lengkap"""
    status: str
    ticker: str
    generated_at: str
    data: Optional[dict] = None
    error: Optional[str] = None


class SentimentResponse(BaseModel):
    """Response model untuk sentimen"""
    ticker: str
    sentiment: Optional[dict] = None
    recommendations: Optional[List[dict]] = None


class CacheResponse(BaseModel):
    """Response model untuk cache operation"""
    status: str
    message: Optional[str] = None


# ==================== CONFIGURATION ====================
app = FastAPI(
    title="Business Intelligence API",
    description="API untuk analisis pasar dan sentiment",
    version="1.0.0"
)

# CORS - Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ERROR HANDLERS ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": str(exc),
            "message": "Internal server error"
        }
    )


# ==================== ROOT ====================
@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "name": "Business Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/api/bi?ticker=AAPL",
            "stock": "/api/stock?ticker=AAPL",
            "news": "/api/news",
            "health": "/health",
            "cache_clear": "/api/cache/clear"
        }
    }


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cache_dir": "cache/"
    }


# ==================== API ENDPOINTS ====================

# Endpoint utama: Analisis Lengkap
@app.get("/api/bi")
async def analyze_stock(
    ticker: str = Query(..., min_length=1, max_length=10),
    force_refresh: bool = Query(False)
):
    """
    Endpoint utama: Analisis lengkap
    """
    try:
        # Normalisasi ticker
        ticker_upper = ticker.upper()
        
        # Validasi Regex (Pastikan 'import re' ada di paling atas)
        if not re.match(r'^[A-Z0-9.\-]+$', ticker_upper):
            raise HTTPException(status_code=400, detail="Invalid ticker format")

        # Jalankan BI Engine
        engine = BIEngine(ticker_upper)
        result = engine.run()

        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail="Analysis failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Endpoint: Hanya data stock
@app.get("/api/stock", response_model=StockResponse)
async def get_stock_data(
    ticker: Annotated[str, Query(..., min_length=1, max_length=10)],
    days: Annotated[int, Query(7, ge=1, le=30)] = 7
) -> dict:
    """Ambil hanya data harga saham"""
    # Validasi ticker
    if not re.match(r'^[A-Z0-9.\-]+$', ticker.upper()):
        raise HTTPException(
            status_code=422,
            detail="Invalid ticker format"
        )

    try:
        data = StockDataCollector.get_closing_prices(ticker.upper(), days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Hanya berita
@app.get("/api/news", response_model=NewsResponse)
async def get_news(
    source: Annotated[str, Query("cnbc")] = "cnbc"
) -> dict:
    """Ambil hanya berita terbaru"""
    try:
        data = NewsScraper.get_world_markets_news()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Skor sentimen saja
@app.get("/api/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    ticker: Annotated[str, Query(..., min_length=1, max_length=10)]
) -> dict:
    """Ambil hanya skor sentimen"""
    if not re.match(r'^[A-Z0-9.\-]+$', ticker.upper()):
        raise HTTPException(
            status_code=422,
            detail="Invalid ticker format"
        )

    try:
        engine = BIEngine(ticker.upper())
        result = engine.run()

        if result.get("status") == "success":
            return {
                "ticker": ticker.upper(),
                "sentiment": result["data"]["sentiment"],
                "recommendations": result["data"]["recommendations"]
            }
        else:
            raise HTTPException(status_code=400, detail="Analysis failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Rekomendasi saja
@app.get("/api/recommendations")
async def get_recommendations(
    ticker: Annotated[str, Query(..., min_length=1, max_length=10)]
) -> dict:
    """Ambil strategi rekomendasi"""
    if not re.match(r'^[A-Z0-9.\-]+$', ticker.upper()):
        raise HTTPException(
            status_code=422,
            detail="Invalid ticker format"
        )

    try:
        engine = BIEngine(ticker.upper())
        result = engine.run()

        if result.get("status") == "success":
            return {
                "ticker": ticker.upper(),
                "sentiment": result["data"]["sentiment"],
                "recommendations": result["data"]["recommendations"],
                "analysis": result["data"]["analysis"]["quantitative_analysis"]
            }
        else:
            raise HTTPException(status_code=400, detail="Analysis failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Hapus cache
@app.post("/api/cache/clear", response_model=CacheResponse)
async def clear_cache() -> dict:
    """Hapus semua cache"""
    try:
        CacheManager.clear_all()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: List ticker yang di-cache
@app.get("/api/cache/list")
async def list_cache() -> dict:
    """List semua cache yang tersedia"""
    try:
        caches = CacheManager.list_caches()
        return {"status": "success", "caches": caches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== POST ENDPOINTS ====================

# Endpoint untuk batch analysis
@app.post("/api/batch")
async def batch_analyze(
    tickers: Annotated[List[str], Body(
        ...,
        min_length=1,
        max_length=10,
        examples=[["AAPL", "MSFT", "GOOGL"]]
    )]
) -> dict:
    """Analisis multiple tickers sekaligus"""
    # Validasi semua ticker
    validated_tickers = []
    for ticker in tickers:
        if not re.match(r'^[A-Z0-9.\-]+$', ticker.upper()):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid ticker format: {ticker}"
            )
        validated_tickers.append(ticker.upper())

    try:
        results = {}
        for ticker in validated_tickers:
            engine = BIEngine(ticker)
            results[ticker] = engine.run()

        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GRAPHQL-LIKE ENDPOINT ====================
@app.post("/api/graphql")
async def graphql_query(
    query: Annotated[GraphQLQuery, Body(...)]
) -> dict:
    """
    GraphQL-style endpoint untuk query fleksibel
    """
    try:
        ticker = query.ticker
        fields = query.fields

        engine = BIEngine(ticker)
        result = engine.run()

        if result.get("status") == "success":
            response = {"ticker": ticker}

            if "stock_data" in fields:
                response["stock_data"] = result["data"]["stock_data"]
            if "news_data" in fields:
                response["news_data"] = result["data"]["news_data"]
            if "sentiment" in fields:
                response["sentiment"] = result["data"]["sentiment"]
            if "recommendations" in fields:
                response["recommendations"] = result["data"]["recommendations"]
            if "analysis" in fields:
                response["analysis"] = result["data"]["analysis"]

            return response
        else:
            raise HTTPException(status_code=400, detail="Analysis failed")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBSOCKET (Optional) ====================
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket untuk real-time updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            ticker = message.get("ticker", "AAPL").upper()

            if not re.match(r'^[A-Z0-9.\-]+$', ticker):
                await websocket.send_text(json.dumps({
                    "error": "Invalid ticker"
                }))
                continue

            engine = BIEngine(ticker)
            result = engine.run()

            await websocket.send_text(json.dumps(result))

    except Exception:
        await websocket.close()


# ==================== MAIN ====================
if __name__ == "__main__":
    import os
    import uvicorn
    
    from datetime import datetime

    # Default port: 8000
    server_port = int(os.environ.get("PORT", 8000))

    print(f"\n{'='*60}")
    print(f"Business Intelligence API Server")
    print(f"Server running at: http://localhost:{server_port}")
    print(f"Docs available at: http://localhost:{server_port}/docs")
    print(f"{'='*60}\n")
    

    uvicorn.run(app, host="0.0.0.0", port=server_port)