"""
Supabase Handler - Database Integration for BI Engine
Handles database operations without using deprecated proxy parameter
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client = None


def get_supabase_client() -> Optional[Any]:
    """
    Get or create Supabase client without deprecated proxy parameter.
    
    Returns:
        Supabase client or None if not available
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    # Try to get credentials from environment
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.info("Supabase credentials not found in environment variables")
        return None
    
    try:
        from supabase import create_client, Client
        
        # Create client WITHOUT proxy parameter (deprecated in supabase>=2.0.0)
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client created successfully")
        return _supabase_client
    
    except Exception as e:
        logger.warning(f"Failed to create Supabase client: {e}")
        return None


def save_analysis_to_supabase(
    ticker: str,
    stock_data: Dict[str, Any],
    news_data: Dict[str, Any],
    analysis: Dict[str, Any],
    sentiment: Dict[str, Any],
    recommendations: List[Dict[str, Any]]
) -> bool:
    """
    Save analysis results to Supabase database.
    
    Args:
        ticker: Stock ticker symbol
        stock_data: Stock data from Yahoo Finance
        news_data: News data from CNBC
        analysis: Market analysis results
        sentiment: Sentiment score results
        recommendations: Business recommendations
    
    Returns:
        True if successful, False otherwise
    """
    client = get_supabase_client()
    
    if client is None:
        logger.debug("Supabase client not available, skipping save")
        return False
    
    try:
        # Prepare data for insertion
        timestamp = int(datetime.now().timestamp())
        
        # Insert stock data
        if stock_data.get("success"):
            client.table("stock_data").insert({
                "ticker": ticker,
                "dates": stock_data.get("data", {}).get("dates", []),
                "closing_prices": stock_data.get("data", {}).get("closing_prices", []),
                "current_price": stock_data.get("data", {}).get("current_price"),
                "price_change": stock_data.get("data", {}).get("price_change"),
                "price_change_percent": stock_data.get("data", {}).get("price_change_percent"),
                "average_price": stock_data.get("data", {}).get("average_price"),
                "highest_price": stock_data.get("data", {}).get("highest_price"),
                "lowest_price": stock_data.get("data", {}).get("lowest_price"),
            }).execute()
        
        # Insert news data
        if news_data.get("success"):
            client.table("news_data").insert({
                "source": news_data.get("source", "CNBC World Markets"),
                "headlines": news_data.get("data", {}).get("headlines", []),
                "total_found": news_data.get("data", {}).get("total_found", 0),
                "relevant_count": news_data.get("data", {}).get("relevant_count", 0),
            }).execute()
        
        # Insert analysis
        client.table("analysis").insert({
            "merged_id": None,  # Could link to merged_data if needed
            "executive_summary": analysis.get("executive_summary", ""),
            "quantitative_analysis": analysis.get("quantitative_analysis", {}),
            "qualitative_analysis": analysis.get("qualitative_analysis", {}),
            "combined_analysis": analysis.get("combined_analysis", {}),
        }).execute()
        
        # Insert sentiment score
        client.table("sentiment_score").insert({
            "score": sentiment.get("score", 5),
            "label": sentiment.get("label", "netral"),
            "quantitative_score": sentiment.get("breakdown", {}).get("quantitative_score", 5),
            "finbert_score": sentiment.get("breakdown", {}).get("finbert_score", 5.0),
            "breakdown": sentiment.get("breakdown", {}),
            "interpretation": sentiment.get("interpretation", ""),
        }).execute()
        
        # Insert recommendations
        for rec in recommendations:
            client.table("recommendations").insert({
                "title": rec.get("title", ""),
                "description": rec.get("description", ""),
                "priority": rec.get("priority", "rendah"),
            }).execute()
        
        logger.info(f"Analysis for {ticker} saved to Supabase successfully")
        return True
    
    except Exception as e:
        logger.warning(f"Failed to save analysis to Supabase: {e}")
        return False


def get_cached_analysis(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get cached analysis from Supabase.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Cached analysis data or None
    """
    client = get_supabase_client()
    
    if client is None:
        return None
    
    try:
        # Get latest stock data
        stock_response = client.table("stock_data").select("*").eq("ticker", ticker).order("created_at", desc=True).limit(1).execute()
        
        if not stock_response.data:
            return None
        
        return stock_response.data[0]
    
    except Exception as e:
        logger.warning(f"Failed to get cached analysis: {e}")
        return None


def clear_supabase_cache() -> bool:
    """
    Clear old cache data from Supabase (older than 24 hours).
    
    Returns:
        True if successful
    """
    client = get_supabase_client()
    
    if client is None:
        return False
    
    try:
        # Call the cleanup function
        client.rpc("cleanup_old_data").execute()
        logger.info("Supabase cache cleared")
        return True
    
    except Exception as e:
        logger.warning(f"Failed to clear Supabase cache: {e}")
        return False


def test_supabase_connection() -> Dict[str, Any]:
    """
    Test Supabase connection.
    
    Returns:
        Connection test result
    """
    client = get_supabase_client()
    
    if client is None:
        return {
            "success": False,
            "message": "Supabase client not available - credentials not found"
        }
    
    try:
        # Simple connection test
        response = client.table("stock_data").select("id").limit(1).execute()
        
        return {
            "success": True,
            "message": "Supabase connection successful"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}"
        }
