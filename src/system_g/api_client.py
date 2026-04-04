# API client module for System-G
# Supports dual-mode operation: MOCK for development, LIVE for production

import logging
import random
from datetime import datetime, timedelta

import pandas as pd
import pyotp
from SmartApi import SmartConnect


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
    """Live API client for Angel One SmartAPI integration."""
    
    def __init__(self, config):
        """
        Initialize connection to Angel One SmartAPI.
        
        Args:
            config: Configuration module with Angel One credentials
        """
        logger.info("Attempting to initialize LiveApiClient...")
        
        self.config = config
        
        # Instantiate SmartConnect client
        self.smart_api = SmartConnect(api_key=config.API_KEY)
        
        # Generate TOTP for authentication
        totp = pyotp.TOTP(config.TOTP_SECRET).now()
        
        # Generate session
        session_data = self.smart_api.generateSession(
            clientCode=config.CLIENT_CODE,
            password=config.PASSWORD,
            totp=totp
        )
        
        if session_data.get("status") is False:
            error_msg = session_data.get("message", "Unknown error during session generation")
            logger.error(f"Session generation failed: {error_msg}")
            raise ConnectionError(f"Failed to connect to Angel One: {error_msg}")
        
        # Store auth token and feed token
        self.auth_token = session_data["data"]["jwtToken"]
        self.refresh_token = session_data["data"]["refreshToken"]
        self.feed_token = self.smart_api.getfeedToken()
        
        logger.info("LiveApiClient initialized and session generated successfully.")
    
    def get_latest_price(self, token):
        """Fetch latest price - Not implemented for Phase 1A."""
        raise NotImplementedError("get_latest_price is not implemented in Phase 1A.")
    
    def submit_order(self, token, qty, side):
        """Submit order - DISABLED for Phase 1A (Listen-Only Mode)."""
        raise NotImplementedError("submit_order is DISABLED in Phase 1A. Listen-Only Mode.")
    
    def get_open_position_qty(self, token):
        """Get open position - DISABLED for Phase 1A (Listen-Only Mode)."""
        raise NotImplementedError("get_open_position_qty is DISABLED in Phase 1A. Listen-Only Mode.")
    
    def get_historical_prices(self, token, lookback_bars):
        """
        Fetch historical price data from Angel One.
        
        Args:
            token: Instrument token (symboltoken)
            lookback_bars: Number of historical bars to fetch
        
        Returns:
            pandas DataFrame with 'close' column
        """
        # Calculate time range for historical data
        to_date = datetime.now()
        # Fetch extra bars to account for market hours
        from_date = to_date - timedelta(days=lookback_bars + 10)
        
        # Format dates as required by Angel One API
        from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
        to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
        
        # Prepare historical data request
        historic_params = {
            "exchange": self.config.EXCHANGE,
            "symboltoken": token,
            "interval": self.config.CANDLE_INTERVAL,
            "fromdate": from_date_str,
            "todate": to_date_str
        }
        
        logger.info(f"[LIVE] Fetching historical data for token {token} from {from_date_str} to {to_date_str}")
        
        # Fetch candle data
        response = self.smart_api.getCandleData(historic_params)
        
        if response.get("status") is False:
            error_msg = response.get("message", "Unknown error fetching historical data")
            logger.error(f"Failed to fetch historical data: {error_msg}")
            raise RuntimeError(f"Historical data fetch failed: {error_msg}")
        
        # Parse response - Angel One returns [timestamp, open, high, low, close, volume]
        candle_data = response.get("data", [])
        
        if not candle_data:
            logger.warning("No historical data returned from API")
            return pd.DataFrame({"close": []})
        
        # Extract close prices and create DataFrame
        # Limit to requested lookback_bars
        close_prices = [candle[4] for candle in candle_data[-lookback_bars:]]
        
        df = pd.DataFrame({"close": close_prices})
        logger.info(f"[LIVE] Successfully fetched {len(df)} historical bars for token {token}")
        
        return df


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
        return LiveApiClient(config)
    else:
        raise ValueError(f"Unrecognized MODE: {config.MODE}. Must be 'MOCK' or 'LIVE'.")
