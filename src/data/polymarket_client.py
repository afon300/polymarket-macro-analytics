import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PolymarketClient:
    """
    Client to fetch data from Polymarket's Gamma API and CLOB API.
    """
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"

    def __init__(self) -> None:
        self.session = requests.Session()
        # Default headers to mimic a browser and avoid basic blocking
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        })

    def get_events(self, limit: int = 20, active: bool = True) -> List[Dict[str, Any]]:
        """
        Fetches a list of events from the Gamma API.
        """
        params = {
            "limit": limit,
            "active": str(active).lower(),
            "closed": "false"
        }
        url = f"{self.GAMMA_API}/events"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch events: {e}")
            return []

    def get_market_history(self, market_id: str, interval: str = "1d") -> pd.DataFrame:
        """
        Fetches the price history for a specific market condition ID from the CLOB API.
        
        Args:
            market_id: The condition ID of the market.
            interval: The time interval (e.g., '1d', '1h').
            
        Returns:
            A pandas DataFrame with the historical prices (probabilities).
        """
        url = f"{self.CLOB_API}/prices-history"
        params = {
            "market": market_id,
            "interval": interval
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "history" not in data or not data["history"]:
                logger.warning(f"No history found for market {market_id}")
                return pd.DataFrame()
                
            # Parse history data
            records = []
            for item in data["history"]:
                records.append({
                    "Date": pd.to_datetime(item["t"], unit="s").tz_localize(None),
                    f"PM_Prob_{market_id[-6:]}": item["p"]
                })
                
            df = pd.DataFrame(records)
            df.set_index("Date", inplace=True)
            
            # Resample to daily frequency (end of day) if 1d was requested
            if interval == "1d":
                df = df.resample('D').last().ffill()
                
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch market history for {market_id}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    client = PolymarketClient()
    events = client.get_events(limit=2)
    print(f"Fetched {len(events)} events.")
    if events and "markets" in events[0] and events[0]["markets"]:
        # Try fetching history for the first market of the first event
        market_id = events[0]["markets"][0]["conditionId"]
        print(f"Fetching history for market: {market_id}")
        df = client.get_market_history(market_id)
        print(df.head())
