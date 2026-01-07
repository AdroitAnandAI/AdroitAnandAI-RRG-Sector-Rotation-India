# RRG Chart Visualization

A Streamlit application for visualizing Relative Rotation Graphs (RRG) for Indian stock market sectors. This application fetches real-time stock data from AngelOne SmartAPI and generates interactive RRG charts for sector analysis.

## Features

- 📊 **Interactive RRG Charts**: Visualize relative strength and momentum of stocks/sectors
- 📅 **Multiple Timeframes**: Support for daily and weekly analysis
- 🏢 **Sector Analysis**: Pre-configured sectors (Banking, IT, Pharma, Auto, FMCG, Energy, Metals, etc.)
- 📈 **Real-time Data**: Fetches live data from AngelOne SmartAPI
- 🎯 **Customizable Settings**: Adjustable window periods, tail counts, and calculation parameters

## Installation

1. Clone or navigate to the project directory:
```bash
cd RRG-Chart-Visualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### AngelOne API Credentials

You need to have an AngelOne SmartAPI account with the following credentials:
- API Key
- Client ID
- Password
- TOTP Token (for 2FA)

These can be entered directly in the Streamlit app sidebar.

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. The application will open in your browser (typically at `http://localhost:8501`)

3. **Setup Steps:**
   - Enter your AngelOne API credentials in the sidebar
   - Click "Save Credentials"
   - Select your preferred timeframe (daily/weekly)
   - Choose a benchmark index (NIFTY 50, NIFTY Bank, etc.)
   - Select a sector and stocks to analyze
   - Click "Generate RRG Chart"

## Understanding RRG Charts

RRG (Relative Rotation Graph) charts plot stocks/sectors in a 2D space:
- **X-axis**: RS Ratio (Relative Strength normalized)
- **Y-axis**: RS Momentum (Rate of Change of RS normalized)

### Quadrants:

1. **Leading** (Top Right): High RS, High Momentum
   - Strong performers with positive momentum
   - Good candidates for continued outperformance

2. **Weakening** (Bottom Right): High RS, Low Momentum
   - Previously strong but losing momentum
   - May be approaching a peak

3. **Lagging** (Bottom Left): Low RS, Low Momentum
   - Weak performers with negative momentum
   - Avoid or consider exiting

4. **Improving** (Top Left): Low RS, High Momentum
   - Weak but gaining strength
   - Potential turnaround candidates

## Project Structure

```
RRG-Chart-Visualization/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── src/
    ├── loaders/
    │   ├── __init__.py
    │   └── AngelOneLoader.py   # Data loader for AngelOne API
    ├── rrg_calculator.py       # RRG calculation logic
    └── sectors.py              # Sector and stock definitions
```

## Customization

### Adding New Sectors

Edit `src/sectors.py` to add new sectors or stocks:

```python
SECTORS = {
    "Your Sector": [
        ("SYMBOL-EQ", "TOKEN"),
        ...
    ]
}
```

### Adjusting Calculation Parameters

In the Streamlit app sidebar, you can adjust:
- **Window**: Moving average window for RS calculation (default: 14)
- **ROC Period**: Period for momentum calculation (default: 52 for weekly, 20 for daily)
- **Tail Count**: Number of historical points to show (default: 4)

## Data Source

This application uses AngelOne SmartAPI to fetch stock data. The data fetching method is similar to:
- `tradesRSI.py` - Uses `getStockData()` function
- `whats1.py` - Uses SmartAPI for market data

## Notes

- Ensure you have sufficient API quota with AngelOne
- Data availability depends on AngelOne API access
- Some stocks may not have sufficient historical data
- Weekly charts require at least 52+ weeks of data for accurate calculations

## Troubleshooting

1. **API Connection Failed**: 
   - Verify your credentials are correct
   - Check if TOTP token is valid
   - Ensure you have API access enabled

2. **No Data Available**:
   - Verify stock symbols and tokens are correct
   - Check if stocks are actively traded
   - Ensure sufficient historical data exists

3. **Chart Not Displaying**:
   - Check browser console for errors
   - Verify all selected stocks have valid data
   - Try reducing the number of stocks

## License

This project is for educational and personal use. Please ensure compliance with AngelOne API terms of service.

## Acknowledgments

- RRG calculation logic adapted from [RRG-Lite](https://github.com/BennyThadikaran/RRG-Lite)
- Data fetching inspired by `tradesRSI.py` and `whats1.py` implementations

