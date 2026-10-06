import pandas as pd
import numpy as np
import scipy.stats as stats
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """
    Engine to compute correlations between Polymarket probabilities and macro indicators.
    """

    def __init__(self) -> None:
        pass

    def merge_datasets(self, poly_df: pd.DataFrame, macro_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merges Polymarket and Macro datasets, aligning dates and handling missing values.
        """
        logger.info("Merging datasets...")
        if poly_df.empty or macro_df.empty:
            logger.warning("One of the datasets is empty.")
            return pd.DataFrame()

        # Merge on Date index
        merged_df = poly_df.join(macro_df, how="inner")
        
        # Forward fill to handle weekends or missing macro data
        merged_df = merged_df.ffill().dropna()
        
        logger.info(f"Merged dataset shape: {merged_df.shape}")
        return merged_df

    def compute_global_correlation(self, df: pd.DataFrame, target_col: str, macro_cols: list[str]) -> Dict[str, Any]:
        """
        Computes Pearson and Spearman correlations between a Polymarket probability and macro indicators.
        
        Args:
            df: The merged DataFrame.
            target_col: The Polymarket probability column name.
            macro_cols: List of macro indicator column names.
            
        Returns:
            A dictionary containing correlation statistics.
        """
        results = {}
        for col in macro_cols:
            if col not in df.columns or target_col not in df.columns:
                continue
                
            # Pearson (linear)
            pearson_corr, pearson_p = stats.pearsonr(df[target_col], df[col])
            
            # Spearman (monotonic)
            spearman_corr, spearman_p = stats.spearmanr(df[target_col], df[col])
            
            results[col] = {
                "pearson_corr": round(pearson_corr, 4),
                "pearson_p_value": round(pearson_p, 4),
                "spearman_corr": round(spearman_corr, 4),
                "spearman_p_value": round(spearman_p, 4),
                "is_significant": spearman_p < 0.05
            }
            
        return results

    def compute_rolling_correlation(self, df: pd.DataFrame, target_col: str, macro_cols: list[str], window: int = 30) -> pd.DataFrame:
        """
        Computes rolling Pearson correlation to observe relationship changes over time.
        """
        rolling_corr_df = pd.DataFrame(index=df.index)
        
        for col in macro_cols:
            if col in df.columns and target_col in df.columns:
                # Calculate rolling correlation
                rolling_corr_df[f"{col}_rolling_corr"] = df[target_col].rolling(window=window).corr(df[col])
                
        return rolling_corr_df.dropna()
