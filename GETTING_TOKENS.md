# How to Get Stock Tokens for RRG Charts

## Method 1: Using Scrip Master JSON

AngelOne provides a scrip master file that contains all stock symbols and their corresponding tokens:

1. Download the scrip master JSON from:
   ```
   https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json
   ```

2. Search for your stock symbol in the JSON file
3. Extract the `token` value for the corresponding symbol

## Method 2: Using AngelOne API

You can query the scrip master programmatically:

```python
import requests
import json

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
data = response.json()

# Search for a symbol
symbol = "HDFCBANK-EQ"
for item in data:
    if item.get("symbol") == symbol and item.get("exch_seg") == "NSE":
        print(f"Symbol: {item['symbol']}, Token: {item['token']}")
        break
```

## Method 3: Using the App

The Streamlit app allows you to:
1. Enter stock symbols manually
2. The app will attempt to fetch tokens (if implemented)
3. Or you can provide tokens directly in the sectors.py file

## Updating sectors.py

To add new stocks or sectors, edit `src/sectors.py`:

```python
SECTORS = {
    "Your Sector": [
        ("SYMBOL-EQ", "TOKEN"),  # Format: (symbol, token)
        ...
    ]
}

BENCHMARKS = {
    "BENCHMARK NAME": ("SYMBOL-EQ", "TOKEN"),
}
```

## Important Notes

- **Token Format**: Tokens are strings of numbers (e.g., "1333", "4963")
- **Symbol Format**: NSE equity symbols end with "-EQ" (e.g., "HDFCBANK-EQ")
- **Exchange**: Most Indian stocks use "NSE" exchange
- **Benchmark Tokens**: Index tokens are typically longer (e.g., "99926000" for NIFTY 50)

## Common Benchmark Tokens

- NIFTY 50: 99926000
- NIFTY BANK: 99926009
- NIFTY IT: 99926010
- NIFTY PHARMA: 99926011
- NIFTY AUTO: 99926012
- NIFTY FMCG: 99926013
- NIFTY ENERGY: 99926014
- NIFTY METAL: 99926015

**Note**: These tokens may change. Always verify from the scrip master JSON.

