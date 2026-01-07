"""
Utility to fetch stock tokens from AngelOne Scrip Master JSON
"""
import requests
import logging

logger = logging.getLogger(__name__)

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

# Cache for scrip master data
_scrip_master_cache = None


def fetch_scrip_master():
    """Fetch and cache scrip master JSON"""
    global _scrip_master_cache
    if _scrip_master_cache is None:
        try:
            response = requests.get(SCRIP_MASTER_URL, timeout=10)
            response.raise_for_status()
            _scrip_master_cache = response.json()
            logger.info("Scrip master JSON fetched successfully")
        except Exception as e:
            logger.error(f"Failed to fetch scrip master: {e}")
            return None
    return _scrip_master_cache


# Hardcoded benchmark tokens (fallback if not found in scrip master)
# These match the exact symbols from OpenAPIScripMaster.json
BENCHMARK_TOKENS = {
    # Exact symbols from scrip master
    "Nifty 50": "99926000",
    "Nifty Bank": "99926009",
    "Nifty IT": "99926008",
    "Nifty Pharma": "99926023",
    "Nifty Auto": "99926029",
    "Nifty FMCG": "99926021",
    "Nifty Energy": "99926020",
    "Nifty Metal": "99926030",
    # Legacy formats for backward compatibility
    "NIFTY50-EQ": "99926000",
    "NIFTYBANK-EQ": "99926009",
    "NIFTYIT-EQ": "99926008",
    "NIFTYPHARMA-EQ": "99926023",
    "NIFTYAUTO-EQ": "99926029",
    "NIFTYFMCG-EQ": "99926021",
    "NIFTYENERGY-EQ": "99926020",
    "NIFTYMETAL-EQ": "99926030",
    # Also try without -EQ suffix
    "NIFTY50": "99926000",
    "NIFTYBANK": "99926009",
    "NIFTYIT": "99926008",
    "NIFTYPHARMA": "99926023",
    "NIFTYAUTO": "99926029",
    "NIFTYFMCG": "99926021",
    "NIFTYENERGY": "99926020",
    "NIFTYMETAL": "99926030",
}


def get_token_from_symbol(symbol, exchange="NSE"):
    """
    Get token for a given symbol from scrip master
    
    :param symbol: Stock symbol (e.g., "HDFCBANK-EQ")
    :param exchange: Exchange (NSE or BSE)
    :return: Token string or None
    """
    # First check hardcoded benchmark tokens
    if symbol in BENCHMARK_TOKENS:
        return BENCHMARK_TOKENS[symbol]
    
    scrip_data = fetch_scrip_master()
    if scrip_data is None:
        # If scrip master fetch fails, try benchmark tokens as fallback
        if symbol in BENCHMARK_TOKENS:
            return BENCHMARK_TOKENS[symbol]
        return None
    
    # Try exact match
    for item in scrip_data:
        if item.get("symbol") == symbol and item.get("exch_seg") == exchange:
            return str(item.get("token"))
    
    # If exact match not found, try without -EQ suffix
    if symbol.endswith("-EQ"):
        base_symbol = symbol[:-3]
        for item in scrip_data:
            if item.get("symbol") == base_symbol and item.get("exch_seg") == exchange:
                return str(item.get("token"))
        
        # Also try with "name" field for NSE (as per jsonReader.py)
        for item in scrip_data:
            if item.get("name") == base_symbol and item.get("exch_seg") == exchange:
                return str(item.get("token"))
    
    # Try fuzzy match on name field for benchmarks (case-insensitive)
    if "NIFTY" in symbol.upper() or "NIFTY" in symbol:
        # Try exact match first (case-insensitive)
        symbol_upper = symbol.upper()
        symbol_lower = symbol.lower()
        symbol_title = symbol.title()  # "Nifty Pharma" format
        
        for item in scrip_data:
            item_name = item.get("name", "")
            item_symbol = item.get("symbol", "")
            # Try multiple case variations
            if ((symbol_upper == item_name.upper() or symbol_upper == item_symbol.upper() or
                 symbol_lower == item_name.lower() or symbol_lower == item_symbol.lower() or
                 symbol_title == item_name or symbol_title == item_symbol or
                 symbol == item_name or symbol == item_symbol) and 
                item.get("exch_seg") == exchange):
                return str(item.get("token"))
        
        # If still not found, try substring match
        symbol_upper_clean = symbol_upper.replace("-EQ", "").replace(" ", "")
        for item in scrip_data:
            item_name = item.get("name", "").upper().replace(" ", "")
            item_symbol = item.get("symbol", "").upper().replace(" ", "")
            if (symbol_upper_clean in item_name or symbol_upper_clean in item_symbol or
                item_name in symbol_upper_clean or item_symbol in symbol_upper_clean) and item.get("exch_seg") == exchange:
                return str(item.get("token"))
    
    logger.warning(f"Token not found for {symbol} on {exchange}")
    return None

