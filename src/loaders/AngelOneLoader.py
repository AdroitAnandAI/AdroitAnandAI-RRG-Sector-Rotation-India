"""
AngelOne SmartAPI Data Loader for RRG Charts
Fetches OHLC data from AngelOne API similar to tradesRSI.py
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import time
from SmartApi import SmartConnect
import pyotp

logger = logging.getLogger(__name__)


class AngelOneLoader:
    """
    A class to load Daily or Weekly timeframe data from AngelOne SmartAPI.
    
    Parameters:
    :param config: Configuration dict with API credentials
    :type config: dict
    :param timeframe: 'daily' or 'weekly'
    :type timeframe: str
    :param end_date: End date upto which date must be returned
    :type end_date: Optional[datetime]
    :param period: Number of periods to return
    """
    
    timeframes = dict(daily="ONE_DAY", weekly="ONE_DAY", monthly="ONE_DAY")  # Use ONE_DAY and resample to weekly/monthly
    
    def __init__(
        self,
        config: dict,
        tf: Optional[str] = "daily",
        end_date: Optional[datetime] = None,
        period: int = 160,
    ):
        self.closed = False
        self.tf = tf if tf else "daily"
        self.end_date = end_date if end_date else datetime.now()
        self.period = period
        
        # Initialize AngelOne API
        self.api_key = config.get("API_KEY")
        self.client_id = config.get("CLIENT_ID")
        self.password = config.get("PASSWORD")
        self.token = config.get("TOTP_TOKEN")
        self.exchange = config.get("EXCHANGE", "NSE")
        
        if not all([self.api_key, self.client_id, self.password, self.token]):
            raise ValueError("Missing required API credentials in config")
        
        self.smartApi = SmartConnect(self.api_key)
        self._login()
        
        # Symbol token mapping - will be populated from scrip master
        self.symbol_token_map = {}
        self._load_symbol_tokens()
    
    def _login(self):
        """Login to AngelOne API"""
        try:
            totp = pyotp.TOTP(self.token).now()
            for i in range(10):
                data = self.smartApi.generateSession(self.client_id, self.password, totp)
                if data.get('status'):
                    break
                time.sleep(2)
            
            if not data.get('status'):
                raise Exception("Failed to login to AngelOne API")
            
            # Get feed token
            self.smartApi.getfeedToken()
            logger.info("Successfully logged in to AngelOne API")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def _load_symbol_tokens(self):
        """Load symbol to token mapping from scrip master"""
        # This would typically load from the scrip master JSON
        # For now, we'll use a simple mapping approach
        # Users can provide tokens directly or we can fetch from API
        pass
    
    def get(self, symbol: str, token: str) -> Optional[pd.DataFrame]:
        """
        Returns OHLC data for symbol as a pandas DataFrame
        
        :param symbol: Instrument symbol (e.g., 'NIFTY50-EQ')
        :param token: Token ID (required)
        :return: DataFrame with OHLC data
        """
        if token is None:
            logger.warning(f"Token not provided for {symbol}. Please provide token.")
            return None
        
        try:
            # Calculate start date based on period and timeframe
            if self.tf == "daily":
                days_back = self.period + 50  # Extra buffer
            elif self.tf == "weekly":
                days_back = (self.period + 10) * 7
            else:  # monthly
                days_back = (self.period + 10) * 30  # Approximate 30 days per month
            
            start_date = self.end_date - timedelta(days=days_back)
            
            interval = self.timeframes.get(self.tf, "ONE_DAY")
            
            historicParam = {
                "exchange": self.exchange,
                "symboltoken": str(token),
                "interval": interval,
                "fromdate": start_date.strftime("%Y-%m-%d %H:%M"),
                "todate": self.end_date.strftime("%Y-%m-%d %H:%M")
            }
            
            data = self.smartApi.getCandleData(historicParam)
            
            if not data or 'data' not in data:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            stock_data = data.get('data', [])
            
            if not stock_data:
                return None
            
            # Convert to DataFrame
            # Format: [timestamp, open, high, low, close, volume]
            # Timestamp may include timezone offset (e.g., "+05:30")
            # Use format='ISO8601' to handle ISO8601 strings with timezone, or let pandas auto-detect
            df_data = []
            for candle in stock_data:
                # Parse date - handle ISO8601 format with timezone offset
                # If format='ISO8601' fails, pandas will auto-detect the format
                try:
                    date_val = pd.to_datetime(candle[0], format='ISO8601')
                except (ValueError, TypeError):
                    # Fall back to auto-detection (handles various formats including timezone)
                    date_val = pd.to_datetime(candle[0])
                
                df_data.append({
                    'Date': date_val,
                    'Open': float(candle[1]),
                    'High': float(candle[2]),
                    'Low': float(candle[3]),
                    'Close': float(candle[4]),
                    'Volume': float(candle[5]) if len(candle) > 5 else 0
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Resample daily data to weekly or monthly if needed
            if self.tf == "weekly":
                # For weekly timeframe, ensure we only use complete weekly candles
                # The last weekly candle should end on the last previous trading day (not on end_date)
                if len(df) > 0:
                    # Get today's date for comparison
                    today = pd.Timestamp.now().normalize()
                    
                    # Get the last trading day from the actual data
                    last_trading_day_in_data = df.index[-1]
                    # Normalize the last trading day for date comparison (handle both Timestamp and datetime)
                    if isinstance(last_trading_day_in_data, pd.Timestamp):
                        last_trading_day_normalized = last_trading_day_in_data.normalize()
                    else:
                        last_trading_day_normalized = pd.Timestamp(last_trading_day_in_data).normalize()
                    
                    # Only exclude today's data if it exists in the dataset AND it's actually today
                    # This ensures the last weekly candle ends on the previous trading day
                    # Example: If today is 3rd Jan 2025 and data includes 3rd Jan, exclude it
                    # so the last weekly candle ends on 2nd Jan 2025
                    # But be conservative - only filter if we have enough data left
                    if last_trading_day_normalized.date() == today.date() and len(df) > 1:
                        # Exclude today's data to ensure last weekly candle ends on previous trading day
                        # Normalize index for comparison (handle timezone-aware timestamps)
                        df_index_normalized = pd.to_datetime(df.index).normalize()
                        # Ensure today has same timezone as df_index
                        if df_index_normalized.tz is not None:
                            today_tz = today.tz_localize(df_index_normalized.tz) if today.tz is None else today.tz_convert(df_index_normalized.tz)
                        else:
                            today_tz = today.tz_localize(None) if today.tz is not None else today
                        df_filtered = df[df_index_normalized < today_tz]
                        # Only use filtered data if we still have at least some data left
                        # Otherwise, use all data (better to show data than nothing)
                        if len(df_filtered) < 10:  # Need at least 10 days for meaningful weekly data
                            df_filtered = df
                    else:
                        # Data doesn't include today, or we don't have enough data to filter safely
                        # Use all data
                        df_filtered = df
                    
                    # Resample to weekly candles (week ending Friday, starting Monday)
                    df_weekly = df_filtered.resample('W-FRI').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()
                    
                    # Store the last trading day from filtered data for validation
                    if len(df_filtered) > 0:
                        last_trading_day = df_filtered.index[-1]
                        last_trading_day_normalized = pd.Timestamp(last_trading_day).normalize()
                        
                        # Remove incomplete weekly candles
                        # The last weekly candle should include the last trading day
                        # Weekly candles resampled with 'W-FRI' have index as Friday (end of week)
                        if len(df_weekly) > 0:
                            # Get the last weekly candle's end date (index is the end of the week, Friday)
                            last_weekly_date = df_weekly.index[-1]
                            last_weekly_date_normalized = pd.Timestamp(last_weekly_date).normalize()
                            
                            # Calculate days difference between last weekly candle end and last trading day
                            # If the last weekly candle ends more than 2 days after the last trading day,
                            # it means the week is incomplete and should be removed
                            # For Friday-ending weeks, if last trading day is before Friday, the week is incomplete
                            days_diff = (last_weekly_date_normalized - last_trading_day_normalized).days
                            
                            # If the last weekly candle ends more than 2 days after the last trading day,
                            # remove it as it's an incomplete week
                            # This ensures the last weekly candle ends on or very close to the last trading day
                            if days_diff > 2:
                                df_weekly = df_weekly.iloc[:-1]
                    
                    df = df_weekly
                    
                    if len(df) == 0:
                        logger.warning(f"No complete weekly data after filtering for {symbol}")
                        return None
                else:
                    logger.warning(f"No data to resample for {symbol} (weekly)")
                    return None
            elif self.tf == "monthly":
                # Resample to monthly (month end)
                if len(df) > 0:
                    df = df.resample('M').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()
                else:
                    logger.warning(f"No data to resample for {symbol} (monthly)")
                    return None
            
            # Limit to requested period
            if len(df) > self.period:
                df = df.iloc[-self.period:]
            
            # Check if we have enough data
            if len(df) == 0:
                logger.warning(f"No data after processing for {symbol}")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def close(self):
        """Close API session"""
        if not self.closed:
            try:
                self.smartApi.terminateSession(self.client_id)
                self.closed = True
                logger.info("AngelOne API session closed")
            except Exception as e:
                logger.error(f"Error closing session: {e}")

