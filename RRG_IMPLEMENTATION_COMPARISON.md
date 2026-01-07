# RRG Implementation Comparison

## Current Implementation vs Standard RRG (JdK - Julius de Kempenaer)

### Overview
The current implementation follows the RRG-Lite approach, which is based on Julius de Kempenaer's Relative Rotation Graph methodology.

### Formula Comparison

#### 1. Relative Strength (RS) Ratio Calculation

**Current Implementation:**
```python
rs = (stock_df / benchmark_df) * 100
rs_sma = rs.rolling(window=self.window)
rs_normalized = ((rs - rs_sma.mean()) / rs_sma.std(ddof=1)).dropna() + 100
```

**Standard JdK Formula:**
- Calculate RS = (Stock Price / Benchmark Price) × 100
- Calculate SMA of RS over a window period (default: 14)
- Normalize: (RS - SMA(RS)) / StdDev(SMA(RS)) + 100

**Status:** ✅ **MATCHES** - The implementation correctly follows the JdK RS-Ratio formula.

#### 2. Relative Strength Momentum Calculation

**Current Implementation:**
```python
base_rs = rs_ratio.shift(self.period)
rs_roc = ((rs_ratio / base_rs) - 1) * 100
roc_sma = rs_roc.rolling(window=self.window)
momentum = ((rs_roc - roc_sma.mean()) / roc_sma.std(ddof=1)).dropna() + 100
```

**Standard JdK Formula:**
- Calculate ROC (Rate of Change) of RS Ratio: ((RS_ratio(t) / RS_ratio(t-period)) - 1) × 100
- Calculate SMA of ROC over a window period (default: 14)
- Normalize: (ROC - SMA(ROC)) / StdDev(SMA(ROC)) + 100

**Status:** ✅ **MATCHES** - The implementation correctly follows the JdK RS-Momentum formula.

### Key Parameters

| Parameter | Default (Weekly) | Default (Daily) | Description |
|-----------|-----------------|-----------------|-------------|
| Window | 14 | 14 | Period for SMA calculation |
| Period | 52 | 20 | Period for ROC calculation (weeks/days) |

**Note:** The period parameter for ROC should be adjusted based on timeframe:
- Weekly: 52 weeks (1 year)
- Daily: ~20-26 days (approximately 1 month)

### Quadrant Definitions

The quadrants are correctly defined:

1. **Leading (Top-Right)**: RS > 100, Momentum > 100
   - Strong relative strength and positive momentum
   - Color: Green (#008217)

2. **Weakening (Bottom-Right)**: RS > 100, Momentum ≤ 100
   - Strong relative strength but negative momentum
   - Color: Yellow (#918000)

3. **Lagging (Bottom-Left)**: RS ≤ 100, Momentum ≤ 100
   - Weak relative strength and negative momentum
   - Color: Red (#E0002B)

4. **Improving (Top-Left)**: RS ≤ 100, Momentum > 100
   - Weak relative strength but positive momentum
   - Color: Blue (#00749D)

**Status:** ✅ **MATCHES** - Quadrant definitions are correct.

### Differences from Standard RRG

#### 1. **No Major Formula Differences**
The core formulas match the standard JdK implementation. The current code correctly:
- Calculates RS ratio as stock/benchmark × 100
- Normalizes using z-score (standard deviation normalization)
- Adds 100 as base value for centering

#### 2. **Potential Variations (Not Currently Implemented)**

Some RRG implementations may use:
- **Alternative normalization methods**: Some use percentile ranking instead of z-score
- **Different period calculations**: Some use fixed periods regardless of timeframe
- **SMA crossover method**: Some implementations use RS crossover of 10 and 30 SMA (mentioned in RRG-Lite README as an alternative)

#### 3. **Current Implementation Strengths**
- ✅ Correct z-score normalization
- ✅ Proper handling of missing data
- ✅ Series alignment and deduplication
- ✅ Configurable window and period parameters

### Recommendations

1. **Period Adjustment**: Ensure ROC period is appropriate for timeframe:
   - Weekly: 52 (1 year)
   - Daily: 20-26 (approximately 1 month)

2. **Data Quality**: Ensure sufficient historical data:
   - Minimum: window × 2 + period + tail_count
   - Recommended: At least 200+ periods for reliable calculations

3. **Benchmark Selection**: Use appropriate benchmark:
   - For NSE stocks: NIFTY 50
   - For sector analysis: Corresponding sector index

### Conclusion

The current implementation **correctly follows the standard JdK RRG methodology**. The formulas for RS Ratio and RS Momentum match the standard implementation. The main areas for optimization are:
- Ensuring proper period settings for different timeframes
- Handling edge cases with insufficient data
- Providing clear visualization of the rotational movement





