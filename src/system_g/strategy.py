# Trading strategy implementation
# Phase 0: Moving Average Crossover strategy for testing

import logging

import pandas as pd


logger = logging.getLogger("system_g")


class MovingAverageCrossover:
    """Simple moving average crossover strategy for testing."""
    
    def __init__(self, api_client, instrument_token, short_window, long_window):
        """
        Initialize the strategy with dependencies.
        
        Args:
            api_client: API client instance (MockApiClient or LiveApiClient)
            instrument_token: Token/symbol for the instrument to trade
            short_window: Period for short-term SMA
            long_window: Period for long-term SMA
        """
        self.client = api_client
        self.token = instrument_token
        self.short_window = short_window
        self.long_window = long_window
        logger.info(f"Initialized MovingAverageCrossover strategy: short={short_window}, long={long_window}")
    
    def _fetch_historical_data(self):
        """Fetch historical price data from the API client."""
        # Request enough bars to calculate the long SMA plus a buffer
        lookback_bars = self.long_window + 10
        return self.client.get_historical_prices(self.token, lookback_bars)
    
    def get_signal(self):
        """
        Calculate trading signal based on SMA crossover.
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        # Fetch historical data
        df = self._fetch_historical_data()
        
        # Check if we have enough data
        if len(df) <= self.long_window:
            logger.warning(f"Insufficient data for SMA calculation. Have {len(df)}, need > {self.long_window}")
            return "HOLD"
        
        # Calculate SMAs
        short_sma = df["close"].rolling(window=self.short_window).mean()
        long_sma = df["close"].rolling(window=self.long_window).mean()
        
        # Get last two values for crossover detection
        short_prev, short_curr = short_sma.iloc[-2], short_sma.iloc[-1]
        long_prev, long_curr = long_sma.iloc[-2], long_sma.iloc[-1]
        
        # Detect crossover
        if short_prev < long_prev and short_curr > long_curr:
            # Golden cross - short SMA crosses above long SMA
            logger.info(f"GOLDEN CROSS detected: Short SMA ({short_curr:.2f}) crossed above Long SMA ({long_curr:.2f})")
            return "BUY"
        
        if short_prev > long_prev and short_curr < long_curr:
            # Death cross - short SMA crosses below long SMA
            logger.info(f"DEATH CROSS detected: Short SMA ({short_curr:.2f}) crossed below Long SMA ({long_curr:.2f})")
            return "SELL"
        
        return "HOLD"
