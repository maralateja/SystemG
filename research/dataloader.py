"""
DataLoader module for centralized historical data access.

This module provides the DataLoader class which serves as a gateway
for all historical data access in the research environment.
"""

import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger("system_g.research")


class DataLoader:
    """
    Centralized gateway for historical data access in the research environment.
    
    This class handles loading historical price data from local Parquet files
    with an in-memory caching mechanism to prevent redundant file reads.
    
    Attributes:
        data_directory: Path to the directory containing Parquet data files.
        cache: Dictionary storing loaded DataFrames keyed by instrument token.
    
    Example:
        >>> loader = DataLoader("research/data")
        >>> df = loader.load_instrument_data("3045")
        >>> df.head()
    """
    
    def __init__(self, data_directory: str | Path) -> None:
        """
        Initialize the DataLoader with a data directory path.
        
        Args:
            data_directory: Path to the research/data/ folder containing
                Parquet files for each instrument.
        """
        self.data_directory = Path(data_directory)
        self.cache: dict[str, pd.DataFrame] = {}
        
        logger.info(f"DataLoader initialized with data directory: {self.data_directory}")
    
    def load_instrument_data(self, instrument_token: str) -> pd.DataFrame | None:
        """
        Load historical data for a specific instrument.
        
        This method first checks the in-memory cache for the requested data.
        If not cached, it loads the data from the corresponding Parquet file
        and stores it in the cache for future access.
        
        Args:
            instrument_token: The unique identifier for the instrument
                (e.g., "3045" for SBIN).
        
        Returns:
            A pandas DataFrame containing the historical data with columns
            such as timestamp, open, high, low, close, volume. Returns None
            if the data file does not exist.
        """
        # Check cache first
        if instrument_token in self.cache:
            logger.info(f"Fetching {instrument_token} from cache")
            return self.cache[instrument_token]
        
        # Construct file path
        file_path = self.data_directory / f"{instrument_token}.parquet"
        
        # Load from file with error handling
        try:
            dataframe = pd.read_parquet(file_path)
            logger.info(f"Loaded {instrument_token} from file ({len(dataframe)} rows)")
        except FileNotFoundError:
            logger.warning(f"Data file not found: {file_path}")
            return None
        
        # Store in cache
        self.cache[instrument_token] = dataframe
        
        return dataframe
    
    def clear_cache(self, instrument_token: str | None = None) -> None:
        """
        Clear cached data from memory.
        
        Args:
            instrument_token: If provided, clears only the cache for this
                specific instrument. If None, clears the entire cache.
        """
        if instrument_token is None:
            self.cache.clear()
            logger.info("Cleared entire cache")
        elif instrument_token in self.cache:
            del self.cache[instrument_token]
            logger.info(f"Cleared cache for {instrument_token}")
    
    def list_available_instruments(self) -> list[str]:
        """
        List all instruments with available data files.
        
        Returns:
            A list of instrument tokens for which Parquet files exist
            in the data directory.
        """
        parquet_files = self.data_directory.glob("*.parquet")
        return [f.stem for f in parquet_files]
