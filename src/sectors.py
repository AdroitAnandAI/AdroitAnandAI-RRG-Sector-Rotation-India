"""
Sector definitions for Indian stock market
Stock symbols for different sectors
Tokens will be fetched automatically from scrip master JSON
"""
# Format: {sector_name: [symbol, ...]}

SECTORS = {
    "Banking": [
        "HDFCBANK-EQ",
        "ICICIBANK-EQ",
        "SBIN-EQ",
        "KOTAKBANK-EQ",
        "AXISBANK-EQ",
        "INDUSINDBK-EQ",
        "FEDERALBNK-EQ",
        "PNB-EQ",
        "BANKBARODA-EQ",
        "UNIONBANK-EQ",
    ],
    "IT": [
        "TCS-EQ",
        "INFY-EQ",
        "HCLTECH-EQ",
        "TECHM-EQ",
        "WIPRO-EQ",
        "LTIM-EQ",
        "MPHASIS-EQ",
        "PERSISTENT-EQ",
        "COFORGE-EQ",
        "ZENSARTECH-EQ",
    ],
    "Pharma": [
        "SUNPHARMA-EQ",
        "DRREDDY-EQ",
        "CIPLA-EQ",
        "LUPIN-EQ",
        "TORNTPHARM-EQ",
        "GLENMARK-EQ",
        "ZYDUSLIFE-EQ",
        "DIVISLAB-EQ",
        "AUROPHARMA-EQ",
        "BIOCON-EQ",
    ],
    "Auto": [
        "MARUTI-EQ",
        "M&M-EQ",
        "TATAMOTORS-EQ",
        "BAJAJ-AUTO-EQ",
        "HEROMOTOCO-EQ",
        "EICHERMOT-EQ",
        "ASHOKLEY-EQ",
        "TVSMOTOR-EQ",
        "BHARATFORG-EQ",
        "MRF-EQ",
    ],
    "FMCG": [
        "HINDUNILVR-EQ",
        "ITC-EQ",
        "NESTLEIND-EQ",
        "BRITANNIA-EQ",
        "DABUR-EQ",
        "MARICO-EQ",
        "GODREJCP-EQ",
        "COLPAL-EQ",
        "TATACONSUM-EQ",
        "EMAMILTD-EQ",
    ],
    "Energy": [
        "RELIANCE-EQ",
        "ONGC-EQ",
        "IOC-EQ",
        "BPCL-EQ",
        "HINDPETRO-EQ",
        "GAIL-EQ",
        "ADANIENT-EQ",
        "ADANIGREEN-EQ",
        "TATAPOWER-EQ",
        "NTPC-EQ",
    ],
    "Metals": [
        "TATASTEEL-EQ",
        "JSWSTEEL-EQ",
        "SAIL-EQ",
        "VEDL-EQ",
        "HINDALCO-EQ",
        "NMDC-EQ",
        "NATIONALUM-EQ",
        "HINDZINC-EQ",
        "JINDALSAW-EQ",
        "RATNAMANI-EQ",
    ],
    "Telecom": [
        "BHARTIARTL-EQ",
        "RELIANCE-EQ",
        "IDEA-EQ",
    ],
    "Cement": [
        "ULTRACEMCO-EQ",
        "SHREECEM-EQ",
        "ACC-EQ",
        "AMBUJACEM-EQ",
        "DALMIABHA-EQ",
        "RAMCOCEM-EQ",
        "JKLAKSHMI-EQ",
        "ORIENTCEM-EQ",
    ],
    "Real Estate": [
        "DLF-EQ",
        "GODREJPROP-EQ",
        "OBEROIRLTY-EQ",
        "PRESTIGE-EQ",
        "SOBHA-EQ",
        "BRIGADE-EQ",
        "MAHLIFE-EQ",
        "PHOENIXLTD-EQ",
    ],
}

# Benchmark indices
# Format: {name: symbol}
# Tokens will be fetched automatically from scrip master JSON or use hardcoded fallback
# Note: Benchmarks may not have -EQ suffix in scrip master, so we try both formats
BENCHMARKS = {
    "NIFTY 50": "Nifty 50",  # Token: 99926000
    "NIFTY BANK": "Nifty Bank",  # Token: 99926009
    "NIFTY IT": "Nifty IT",  # Token: 99926008
    "NIFTY PHARMA": "Nifty Pharma",  # Token: 99926023
    "NIFTY AUTO": "Nifty Auto",  # Token: 99926029
    "NIFTY FMCG": "Nifty FMCG",  # Token: 99926021
    "NIFTY ENERGY": "Nifty Energy",  # Token: 99926020
    "NIFTY METAL": "Nifty Metal",  # Token: 99926030
}

