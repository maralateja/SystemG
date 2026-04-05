# Configuration settings for System-G
# Copy this file to config.py and fill in your credentials

# =============================================================================
# MODE SWITCHING FLAG
# =============================================================================
# "MOCK" - Uses simulated data and paper trading
# "LIVE" - Uses real market data and executes real trades
MODE = "LIVE"

# =============================================================================
# ANGEL ONE CREDENTIALS
# =============================================================================
API_KEY = "your_api_key_here"           # Your Angel One API Key
USERNAME = "your_username_here"          # Your Angel One Username
PASSWORD = "your_pin_here"               # Your Angel One PIN/Password  
TOTP_SECRET = "your_totp_secret_here"    # Your TOTP secret key for 2FA
CLIENT_CODE = "your_client_code_here"    # Your Angel One Client Code

# =============================================================================
# TRADING PARAMETERS
# =============================================================================
INSTRUMENT_TOKEN = "3045"   # Symbol token for the instrument (e.g., "3045" for SBIN)
EXCHANGE = "NSE"            # Exchange: NSE, BSE, NFO, etc.
CANDLE_INTERVAL = "FIVE_MINUTE"  # ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, etc.
QUANTITY = 1
SHORT_WINDOW = 5
LONG_WINDOW = 20

# =============================================================================
# OPERATIONAL PARAMETERS
# =============================================================================
LOG_FILE = "system_g.log"
LOOP_FREQUENCY_SECONDS = 5
