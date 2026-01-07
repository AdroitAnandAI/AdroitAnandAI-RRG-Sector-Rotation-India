"""
RRG (Relative Rotation Graph) Calculator
Adapted from RRG-Lite implementation
"""
import pandas as pd
import numpy as np
import statistics


class RRGCalculator:
    """
    Calculate Relative Strength (RS) and RS Momentum for RRG charts
    Using the new formula:
    RS = sector_close / nifty50_close
    EMA_RS = RS.ewm(span=m, adjust=False).mean()
    RS_Ratio = 100 * EMA_RS / EMA_RS.rolling(m).mean()
    ROC = (RS_Ratio - RS_Ratio.shift(k)) / RS_Ratio.shift(k)
    EMA_ROC = ROC.ewm(span=m, adjust=False).mean()
    RS_Momentum = 100 + 100 * EMA_ROC
    """
    
    def __init__(self, window=14, period=52, ema_span=14, roc_shift=10, ema_roc_span=14):
        """
        Initialize RRG Calculator
        
        :param window: Window size for rolling mean in RS_Ratio calculation (deprecated, now uses ema_roc_span)
        :param period: Period for ROC calculation (deprecated, kept for compatibility)
        :param ema_span: Span for EMA calculation of RS (deprecated, now uses ema_roc_span)
        :param roc_shift: Shift period for ROC calculation (k, default 10)
        :param ema_roc_span: Span for EMA calculation (m, default 14) - used for both EMA_RS and EMA_ROC
        """
        self.window = window  # Deprecated, kept for compatibility
        self.period = period  # Deprecated, kept for compatibility
        self.ema_span = ema_span  # Deprecated, kept for compatibility
        self.roc_shift = roc_shift  # k: shift period for ROC
        self.ema_roc_span = ema_roc_span  # m: span for EMA of RS and EMA of ROC, and rolling window for RS_Ratio
    
    def calculate_rs(self, stock_df: pd.Series, benchmark_df: pd.Series) -> pd.Series:
        """
        Calculate RS_Ratio using the new formula:
        RS = sector_close / nifty50_close
        EMA_RS = RS.ewm(span=m, adjust=False).mean()
        RS_Ratio = 100 * EMA_RS / EMA_RS.rolling(m).mean()
        
        :param stock_df: Stock close prices
        :param benchmark_df: Benchmark close prices
        :return: RS ratio series
        """
        # Step 1: Calculate RS (without 100 multiplier)
        rs = stock_df / benchmark_df
        
        # Step 2: Calculate EMA_RS with span=m (using ema_roc_span)
        ema_rs = rs.ewm(span=self.ema_roc_span, adjust=False).mean()
        
        # Step 3: Calculate RS_Ratio using rolling window=m
        ema_rs_mean = ema_rs.rolling(window=self.ema_roc_span).mean()
        rs_ratio = 100 * ema_rs / ema_rs_mean.replace(0, np.nan)
        
        return rs_ratio
    
    def calculate_momentum(self, rs_ratio: pd.Series) -> pd.Series:
        """
        Calculate RS_Momentum using the new formula:
        ROC = (RS_Ratio - RS_Ratio.shift(k)) / RS_Ratio.shift(k)
        EMA_ROC = ROC.ewm(span=m, adjust=False).mean()
        RS_Momentum = 100 + 100 * EMA_ROC
        
        :param rs_ratio: RS ratio series
        :return: RS momentum series
        """
        # Step 1: Calculate ROC
        rs_ratio_shifted = rs_ratio.shift(self.roc_shift)
        roc = (rs_ratio - rs_ratio_shifted) / rs_ratio_shifted.replace(0, np.nan)
        
        # Step 2: Calculate EMA of ROC
        ema_roc = roc.ewm(span=self.ema_roc_span, adjust=False).mean()
        
        # Step 3: Calculate RS_Momentum
        rs_momentum = 100 + 100 * ema_roc
        
        return rs_momentum
    
    def process_series(self, ser: pd.Series) -> pd.Series:
        """
        Make corrections in series if there are duplicate indices
        or not sorted in correct order
        
        :param ser: Input series
        :return: Processed series
        """
        if ser.index.has_duplicates:
            ser = ser.loc[~ser.index.duplicated()]
        
        if not ser.index.is_monotonic_increasing:
            ser = ser.sort_index(ascending=True)
        
        return ser
    
    def get_quadrant(self, rs_value: float, momentum_value: float) -> str:
        """
        Determine which quadrant a point is in
        
        :param rs_value: RS ratio value
        :param momentum_value: RS momentum value
        :return: Quadrant name
        """
        if rs_value > 100 and momentum_value > 100:
            return "Leading"
        elif rs_value > 100 and momentum_value <= 100:
            return "Weakening"
        elif rs_value <= 100 and momentum_value > 100:
            return "Improving"
        else:
            return "Lagging"
    
    def get_color(self, rs_value: float, momentum_value: float) -> str:
        """
        Get color based on quadrant
        
        :param rs_value: RS ratio value
        :param momentum_value: RS momentum value
        :return: Hex color code
        """
        if rs_value > 100:
            return "#008217" if momentum_value > 100 else "#918000"  # Green or Yellow
        else:
            return "#00749D" if momentum_value > 100 else "#E0002B"  # Blue or Red

