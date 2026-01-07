"""
Scrip Master Search Utility
Fetches and searches indices, stocks, and ETFs from OpenAPIScripMaster.json
"""
import requests
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

# Cache for scrip master data
_scrip_master_cache = None

def clear_scrip_master_cache():
    """Clear the scrip master cache (useful for testing or forcing refresh)"""
    global _scrip_master_cache
    _scrip_master_cache = None


def fetch_scrip_master():
    """Fetch and cache scrip master JSON"""
    global _scrip_master_cache
    if _scrip_master_cache is None:
        try:
            response = requests.get(SCRIP_MASTER_URL, timeout=30)  # Increased timeout
            response.raise_for_status()
            _scrip_master_cache = response.json()
            if _scrip_master_cache:
                logger.info(f"Scrip master JSON fetched successfully: {len(_scrip_master_cache)} items")
            else:
                logger.warning("Scrip master JSON is empty")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch scrip master (network error): {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch scrip master: {e}")
            return None
    return _scrip_master_cache


def get_indices(exchange="NSE") -> List[Dict]:
    """
    Get all indices from scrip master
    
    :param exchange: Exchange (NSE or BSE)
    :return: List of index dictionaries with symbol, name, token
    """
    scrip_data = fetch_scrip_master()
    if scrip_data is None:
        return []
    
    indices = []
    for item in scrip_data:
        # Indices have instrumenttype "AMXIDX" and typically contain "NIFTY" in name
        if (item.get("exch_seg") == exchange and 
            item.get("instrumenttype") == "AMXIDX"):
            indices.append({
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "token": str(item.get("token")),
                "exchange": item.get("exch_seg")
            })
    
    # Sort by name
    indices.sort(key=lambda x: x["name"])
    return indices


def get_stocks(exchange="NSE") -> List[Dict]:
    """
    Get all stocks from scrip master
    
    :param exchange: Exchange (NSE or BSE)
    :return: List of stock dictionaries with symbol, name, token
    """
    scrip_data = fetch_scrip_master()
    if scrip_data is None:
        return []
    
    stocks = []
    for item in scrip_data:
        # Stocks have symbol ending with "-EQ" and instrumenttype is empty string or "EQ"
        # Note: In the actual JSON, stocks have instrumenttype as empty string "", not "EQ"
        inst_type = item.get("instrumenttype", "")
        symbol = item.get("symbol", "")
        
        if (item.get("exch_seg") == exchange and 
            symbol.endswith("-EQ") and
            (inst_type == "" or inst_type == "EQ")):
            # Exclude ETFs (they have "ETF" or "BEES" in name/symbol)
            name_upper = item.get("name", "").upper()
            symbol_upper = symbol.upper()
            is_etf = ("ETF" in name_upper or "BEES" in name_upper or 
                     "ETF" in symbol_upper or "BEES" in symbol_upper)
            
            if not is_etf:
                stocks.append({
                    "symbol": symbol,
                    "name": item.get("name"),
                    "token": str(item.get("token")),
                    "exchange": item.get("exch_seg")
                })
    
    # Sort by name
    stocks.sort(key=lambda x: x["name"])
    return stocks


def get_etfs(exchange="NSE") -> List[Dict]:
    """
    Get all ETFs from scrip master
    ETFs are identified by having "ETF" or "BEES" in name/symbol and instrumenttype is empty or EQ
    
    :param exchange: Exchange (NSE or BSE)
    :return: List of ETF dictionaries with symbol, name, token
    """
    scrip_data = fetch_scrip_master()
    if scrip_data is None:
        return []
    
    etfs = []
    for item in scrip_data:
        name_upper = item.get("name", "").upper()
        symbol_upper = item.get("symbol", "").upper()
        inst_type = item.get("instrumenttype", "")
        
        # ETFs have "ETF" or "BEES" in name/symbol and instrumenttype is empty or EQ
        if (item.get("exch_seg") == exchange and 
            (inst_type == "" or inst_type == "EQ") and
            item.get("symbol", "").endswith("-EQ") and
            ("ETF" in name_upper or "BEES" in name_upper or "ETF" in symbol_upper or "BEES" in symbol_upper)):
            etfs.append({
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "token": str(item.get("token")),
                "exchange": item.get("exch_seg")
            })
    
    # Sort by name
    etfs.sort(key=lambda x: x["name"])
    return etfs


def search_indices(query: str, exchange="NSE", limit: int = 50) -> List[Dict]:
    """
    Search indices by name or symbol
    
    :param query: Search query
    :param exchange: Exchange (NSE or BSE)
    :param limit: Maximum results to return
    :return: List of matching indices
    """
    if not query:
        return []
    
    try:
        scrip_data = fetch_scrip_master()
        if scrip_data is None:
            logger.warning("Scrip master data is None")
            return []
        
        query_upper = query.upper().strip()
        if not query_upper:
            return []
        
        results = []
        
        # Search directly in scrip master for better performance
        for item in scrip_data:
            try:
                # Check exchange and instrument type
                if item.get("exch_seg") != exchange:
                    continue
                
                # Indices have instrumenttype "AMXIDX"
                if item.get("instrumenttype") != "AMXIDX":
                    continue
                
                symbol = item.get("symbol", "")
                name = item.get("name", "")
                symbol_upper = symbol.upper()
                name_upper = name.upper()
                
                # Multiple matching strategies
                matches = (
                    query_upper in symbol_upper or  # Query in symbol
                    query_upper in name_upper or  # Query in name
                    symbol_upper.startswith(query_upper) or  # Symbol starts with query
                    name_upper.startswith(query_upper)  # Name starts with query
                )
                
                if matches:
                    results.append({
                        "symbol": symbol,
                        "name": name,
                        "token": str(item.get("token")),
                        "exchange": item.get("exch_seg")
                    })
                    if len(results) >= limit:
                        break
            except Exception as e:
                logger.debug(f"Error processing index item: {e}")
                continue
        
        # If no results, try fallback using get_indices()
        if not results:
            try:
                all_indices = get_indices(exchange)
                for idx in all_indices:
                    if (query_upper in idx["name"].upper() or 
                        query_upper in idx["symbol"].upper()):
                        results.append(idx)
                        if len(results) >= limit:
                            break
            except Exception as e2:
                logger.error(f"Error in get_indices() fallback: {e2}")
        
        logger.info(f"search_indices('{query}') returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in search_indices: {e}")
        return []


def search_stocks(query: str, exchange="NSE", limit: int = 50) -> List[Dict]:
    """
    Search stocks by name or symbol
    
    :param query: Search query
    :param exchange: Exchange (NSE or BSE)
    :return: List of matching stocks
    """
    if not query:
        return []
    
    try:
        scrip_data = fetch_scrip_master()
        if scrip_data is None:
            logger.warning("Scrip master data is None")
            return []
        
        query_upper = query.upper().strip()
        if not query_upper:
            return []
        
        results = []
        
        # Remove -EQ suffix from query if present for better matching
        query_base = query_upper.replace("-EQ", "")
        
        # Search directly in scrip master for better performance
        for item in scrip_data:
            try:
                # Check exchange
                if item.get("exch_seg") != exchange:
                    continue
                
                inst_type = item.get("instrumenttype", "")
                symbol = item.get("symbol", "")
                
                # Stocks have symbol ending with "-EQ" and instrumenttype is empty string or "EQ"
                # Note: In the actual JSON, stocks have instrumenttype as empty string "", not "EQ"
                if not symbol.endswith("-EQ") or (inst_type != "" and inst_type != "EQ"):
                    continue
                
                # Exclude ETFs (they have "ETF" or "BEES" in name/symbol)
                name_upper = item.get("name", "").upper()
                symbol_upper = symbol.upper()
                is_etf = ("ETF" in name_upper or "BEES" in name_upper or 
                         "ETF" in symbol_upper or "BEES" in symbol_upper)
                if is_etf:
                    continue
                
                symbol_upper = symbol.upper()
                name_upper = item.get("name", "").upper()
                
                # Remove -EQ from symbol for matching
                symbol_base = symbol_upper.replace("-EQ", "")
                
                # Multiple matching strategies:
                # 1. Exact match (case-insensitive)
                # 2. Query in symbol base (e.g., "HDFCBANK" in "HDFCBANK-EQ" -> "HDFCBANK")
                # 3. Query in name
                # 4. Symbol starts with query
                # 5. Name starts with query
                # 6. Symbol base equals query base
                
                matches = (
                    symbol_upper == query_upper or  # Exact symbol match
                    symbol_base == query_base or  # Base symbol match
                    query_upper in symbol_upper or  # Query in symbol
                    query_base in symbol_base or  # Query base in symbol base
                    symbol_base.startswith(query_base) or  # Symbol starts with query
                    query_upper in name_upper or  # Query in name
                    name_upper.startswith(query_upper)  # Name starts with query
                )
                
                if matches:
                    results.append({
                        "symbol": symbol,
                        "name": item.get("name"),
                        "token": str(item.get("token")),
                        "exchange": item.get("exch_seg")
                    })
                    if len(results) >= limit:
                        break
            except Exception as e:
                # Skip items that cause errors
                logger.debug(f"Error processing item: {e}")
                continue
        
        # If no results found, try fallback using get_stocks()
        if not results:
            logger.debug(f"No results from direct search for '{query}', trying get_stocks() fallback")
            try:
                all_stocks = get_stocks(exchange)
                logger.debug(f"get_stocks() returned {len(all_stocks)} stocks")
                
                for stock in all_stocks:
                    symbol_upper = stock["symbol"].upper()
                    name_upper = stock["name"].upper()
                    symbol_base = symbol_upper.replace("-EQ", "")
                    
                    if (query_upper in symbol_upper or 
                        query_base in symbol_base or
                        symbol_base.startswith(query_base) or
                        query_upper in name_upper or
                        name_upper.startswith(query_upper)):
                        results.append(stock)
                        if len(results) >= limit:
                            break
            except Exception as e2:
                logger.error(f"Error in get_stocks() fallback: {e2}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"search_stocks('{query}') returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in search_stocks: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def search_etfs(query: str, exchange="NSE", limit: int = 50) -> List[Dict]:
    """
    Search ETFs by name or symbol
    
    :param query: Search query
    :param exchange: Exchange (NSE or BSE)
    :param limit: Maximum results to return
    :return: List of matching ETFs
    """
    if not query:
        return []
    
    try:
        scrip_data = fetch_scrip_master()
        if scrip_data is None:
            logger.warning("Scrip master data is None")
            return []
        
        query_upper = query.upper().strip()
        if not query_upper:
            return []
        
        results = []
        
        # Search directly in scrip master for better performance
        for item in scrip_data:
            try:
                # Check exchange
                if item.get("exch_seg") != exchange:
                    continue
                
                inst_type = item.get("instrumenttype", "")
                symbol = item.get("symbol", "")
                name_upper = item.get("name", "").upper()
                symbol_upper = symbol.upper()
                
                # ETFs have "ETF" or "BEES" in name/symbol and instrumenttype is empty or EQ
                is_etf = (
                    (inst_type == "" or inst_type == "EQ") and
                    symbol.endswith("-EQ") and
                    ("ETF" in name_upper or "BEES" in name_upper or "ETF" in symbol_upper or "BEES" in symbol_upper)
                )
                
                if not is_etf:
                    continue
                
                # Multiple matching strategies
                matches = (
                    query_upper in symbol_upper or  # Query in symbol
                    query_upper in name_upper or  # Query in name
                    symbol_upper.startswith(query_upper) or  # Symbol starts with query
                    name_upper.startswith(query_upper)  # Name starts with query
                )
                
                if matches:
                    results.append({
                        "symbol": symbol,
                        "name": item.get("name"),
                        "token": str(item.get("token")),
                        "exchange": item.get("exch_seg")
                    })
                    if len(results) >= limit:
                        break
            except Exception as e:
                logger.debug(f"Error processing ETF item: {e}")
                continue
        
        # If no results, try fallback using get_etfs()
        if not results:
            try:
                all_etfs = get_etfs(exchange)
                for etf in all_etfs:
                    if (query_upper in etf["name"].upper() or 
                        query_upper in etf["symbol"].upper()):
                        results.append(etf)
                        if len(results) >= limit:
                            break
            except Exception as e2:
                logger.error(f"Error in get_etfs() fallback: {e2}")
        
        logger.info(f"search_etfs('{query}') returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in search_etfs: {e}")
        return []


def get_item_by_symbol(symbol: str, exchange="NSE") -> Optional[Dict]:
    """
    Get item by exact symbol match
    
    :param symbol: Symbol to search for
    :param exchange: Exchange (NSE or BSE)
    :return: Item dictionary or None
    """
    scrip_data = fetch_scrip_master()
    if scrip_data is None:
        return None
    
    for item in scrip_data:
        if (item.get("symbol") == symbol and 
            item.get("exch_seg") == exchange):
            return {
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "token": str(item.get("token")),
                "exchange": item.get("exch_seg"),
                "instrumenttype": item.get("instrumenttype")
            }
    
    return None

