# 📈 Polymarket Macro Correlation Engine

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

A quantitative analysis tool designed to bridge the gap between predictive markets (Polymarket) and traditional macroeconomic indicators. This engine fetches historical probabilities from prediction markets and correlates them with crypto assets (BTC), forex (EUR/USD), and equities (SP500, VIX) to identify non-obvious market relationships.

## 🚀 Features

- **Automated Data Ingestion:** Interfaces with Polymarket's Gamma/CLOB API and Yahoo Finance (`yfinance`) for seamless historical data retrieval.
- **Statistical Correlation Engine:** Computes Pearson and Spearman rank correlation coefficients, including p-value significance testing, to validate macro relationships.
- **Rolling Analysis:** Tracks rolling correlations to identify regime shifts and decoupling events between predictive sentiment and macro reality.
- **Interactive Dashboard:** Built with Streamlit and Plotly for high-performance, interactive data visualization.

## 🛠️ Tech Stack

- **Data Processing:** `pandas`, `numpy`
- **Statistics:** `scipy`, `statsmodels`
- **APIs:** `requests`, `yfinance`
- **Visualization:** `streamlit`, `plotly`
- **Tooling:** `ruff` (linting/formatting), `mypy` (type checking), `pytest`

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/afon300/polymarket-macro-analytics.git
   cd polymarket-macro-analytics
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Usage

To launch the interactive Streamlit dashboard:

```bash
streamlit run src/dashboard/app.py
```

From the dashboard, you can:
1. Select an active Polymarket event.
2. Choose macro indicators to compare against (e.g., BTC, SP500, VIX).
3. Adjust the lookback period and instantly visualize the statistical correlations and normalized price trends.

## 🧪 Development

This project uses strict type checking and linting to ensure code quality.

```bash
# Run linter & formatter
ruff check .
ruff format .

# Run type checker
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
