# API client module for System-G
# Supports dual-mode operation: MOCK for development, LIVE for production

import logging
import random

import pandas as pd


logger = logging.getLogger("system_g")


class MockApiClient:
    """Mock API client for development and testing."""
    
    def __init__(self):
        self._position = 0
        self._last_price = 100.0
        logger.info("Initialized in MOCK mode.")
    
    def get_latest_price(self, token):
        """Simulate price movement with random fluctuation."""
        self._last_price = self._last_price * random.uniform(0.99, 1.01)
        logger.info(f"[MOCK] Fetched price for {token}: {self._last_price:.2f}")
        return self._last_price
    
    def submit_order(self, token, qty, side):
        """Simulate order submission."""
        if side == "BUY":
            self._position += qty
        elif side == "SELL":
            self._position -= qty
        
        logger.info(f"[MOCK] Submitted {side} order for {qty} units of {token}. New position: {self._position}")
        return {"status": "success"}
    
    def get_open_position_qty(self, token):
        """Return current simulated position."""
        logger.info(f"[MOCK] Current position for {token}: {self._position}")
        return self._position
    
    def get_historical_prices(self, token, lookback_bars):
        """Generate simulated historical price data."""
        prices = [self._last_price]
        for _ in range(lookback_bars - 1):
            prices.append(prices[-1] * random.uniform(0.99, 1.01))
        
        df = pd.DataFrame({"close": prices})
        logger.info(f"[MOCK] Generated {lookback_bars} historical bars for {token}")
        return df


class LiveApiClient:
    """Live API client placeholder for Angel One integration."""
    
    def __init__(self):
        logger.info("Attempting to initialize LiveApiClient...")
        raise NotImplementedError("LiveApiClient is not yet implemented.")
    
    def get_latest_price(self, token):
        raise NotImplementedError
    
    def submit_order(self, token, qty, side):
        raise NotImplementedError
    
    def get_open_position_qty(self, token):
        raise NotImplementedError
    
    def get_historical_prices(self, token, lookback_bars):
        raise NotImplementedError


def get_api_client(config):
    """
    Factory function to return the appropriate API client based on config.MODE.
    
    Args:
        config: Configuration module with MODE attribute
    
    Returns:
        MockApiClient or LiveApiClient instance
    
    Raises:
        ValueError: If config.MODE is not recognized
    """
    if config.MODE == "MOCK":
        return MockApiClient()
    elif config.MODE == "LIVE":
        return LiveApiClient()
    else:
        raise ValueError(f"Unrecognized MODE: {config.MODE}. Must be 'MOCK' or 'LIVE'.")
