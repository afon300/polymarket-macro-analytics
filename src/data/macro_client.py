import yfinance as yf
import pandas as pd
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MacroDataClient:
    """
    Client to fetch macroeconomic and crypto data using Yahoo Finance.
    """
    
    # Common tickers used for macro analysis
    DEFAULT_TICKERS = {
        "BTC": "BTC-USD",
        "SP500": "^GSPC",
        "VIX": "^VIX",
        "GOLD": "GC=F",
        "EURUSD": "EURUSD=X"
    }

    def __init__(self) -> None:
        pass

    def fetch_historical_data(self, ticker: str, start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetches historical daily close prices for a given ticker.
        
        Args:
            ticker: The Yahoo Finance ticker symbol.
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format. Defaults to today.
            
        Returns:
            A pandas DataFrame with 'Date' as index and 'Close' price.
        """
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date or 'today'}")
        
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if data.empty:
                logger.warning(f"No data found for ticker {ticker}.")
                return pd.DataFrame()
            
            # Keep only the Close price and format the index
            df = data[['Close']].copy()
            df.columns = [ticker] # Rename column to the ticker name
            df.index = pd.to_datetime(df.index).tz_localize(None) # Remove timezone for easier merging later
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_multiple(self, tickers: list[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetches and merges historical data for multiple tickers.
        """
        dfs = []
        for ticker in tickers:
            df = self.fetch_historical_data(ticker, start_date, end_date)
            if not df.empty:
                dfs.append(df)
                
        if not dfs:
            return pd.DataFrame()
            
        # Merge all dataframes on Date index
        merged_df = dfs[0]
        for df in dfs[1:]:
            merged_df = merged_df.join(df, how="outer")
            
        # Forward fill to handle non-trading days (like weekends for stocks)
        merged_df = merged_df.ffill()
        return merged_df

if __name__ == "__main__":
    # Simple test block
    client = MacroDataClient()
    tickers_to_fetch = [client.DEFAULT_TICKERS["BTC"], client.DEFAULT_TICKERS["SP500"]]
    df = client.fetch_multiple(tickers_to_fetch, start_date="2024-01-01")
    print(df.head())
    print(df.tail())
