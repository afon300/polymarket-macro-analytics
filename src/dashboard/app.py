import sys
import os
# Add the project root to the Python path so 'src' can be imported when running via Streamlit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data.macro_client import MacroDataClient
from src.data.polymarket_client import PolymarketClient
from src.analysis.correlations import CorrelationEngine

# Configure page
st.set_page_config(page_title="Polymarket Macro Engine", page_icon="📈", layout="wide")
st.title("📈 Polymarket & Macro Correlation Engine")
st.markdown("Analyze correlations between prediction markets and macroeconomic indicators.")

# Initialize clients
@st.cache_resource
def get_clients():
    return MacroDataClient(), PolymarketClient(), CorrelationEngine()

macro_client, poly_client, corr_engine = get_clients()

# Sidebar for configuration
st.sidebar.header("Configuration")

# 1. Fetch Top Markets
with st.sidebar.expander("1. Select Market", expanded=True):
    try:
        events = poly_client.get_events(limit=10)
        market_options = {}
        for event in events:
            if "markets" in event and event["markets"]:
                for market in event["markets"]:
                    if "conditionId" in market and "question" in market:
                        market_options[market["question"]] = market["conditionId"]
                        
        if not market_options:
            st.error("No active markets found.")
            st.stop()
            
        selected_market_name = st.selectbox("Market", list(market_options.keys()))
        selected_condition_id = market_options[selected_market_name]
    except Exception as e:
        st.error(f"Failed to load markets: {e}")
        st.stop()

# 2. Select Macro Indicators
with st.sidebar.expander("2. Select Indicators", expanded=True):
    indicators = list(macro_client.DEFAULT_TICKERS.keys())
    selected_indicators = st.multiselect("Macro Indicators", indicators, default=["BTC", "SP500"])
    
# 3. Timeframe
with st.sidebar.expander("3. Timeframe", expanded=True):
    lookback_days = st.slider("Lookback period (days)", 30, 365, 90)
    
start_date = (pd.Timestamp.now() - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%d")

# Fetch and process data
if st.sidebar.button("Analyze Correlations", type="primary"):
    with st.spinner("Fetching Polymarket history..."):
        poly_df = poly_client.get_market_history(selected_condition_id, interval="1d")
        
    if poly_df.empty:
        st.error("Not enough historical data for this market.")
    else:
        with st.spinner("Fetching Macro data..."):
            tickers = [macro_client.DEFAULT_TICKERS[i] for i in selected_indicators]
            macro_df = macro_client.fetch_multiple(tickers, start_date=start_date)
            # Rename columns back to human readable
            rename_map = {v: k for k, v in macro_client.DEFAULT_TICKERS.items()}
            macro_df.rename(columns=rename_map, inplace=True)
            
        with st.spinner("Merging and computing..."):
            merged_df = corr_engine.merge_datasets(poly_df, macro_df)
            
            if merged_df.empty:
                st.warning("Could not align dates between Polymarket and Macro data.")
            else:
                poly_col = poly_df.columns[0]
                
                # Global Correlation
                st.subheader("Statistical Correlation (Pearson/Spearman)")
                stats = corr_engine.compute_global_correlation(merged_df, poly_col, selected_indicators)
                
                cols = st.columns(len(selected_indicators))
                for idx, ind in enumerate(selected_indicators):
                    if ind in stats:
                        with cols[idx]:
                            st.metric(label=f"Pearson vs {ind}", value=stats[ind]["pearson_corr"])
                            sig = "✅ Significant" if stats[ind]["is_significant"] else "❌ Not Significant"
                            st.caption(f"Spearman p-value: {stats[ind]['spearman_p_value']} ({sig})")
                
                # Rolling Correlation Chart
                st.subheader("30-Day Rolling Correlation")
                rolling_df = corr_engine.compute_rolling_correlation(merged_df, poly_col, selected_indicators, window=30)
                if not rolling_df.empty:
                    fig_rolling = px.line(rolling_df, title="Rolling Correlation over time")
                    st.plotly_chart(fig_rolling, use_container_width=True)
                
                # Normalized Price Overlay Chart
                st.subheader("Normalized Trends Comparison")
                # Min-Max normalization for comparison
                normalized_df = (merged_df - merged_df.min()) / (merged_df.max() - merged_df.min())
                fig_trends = px.line(normalized_df, title="Normalized Prices (0 to 1 scale)")
                st.plotly_chart(fig_trends, use_container_width=True)
                
                # Raw Data Expander
                with st.expander("View Raw Merged Data"):
                    st.dataframe(merged_df)
