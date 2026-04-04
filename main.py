# Main entry point for System-G

import time

import config
from src.system_g.logger import setup_logger
from src.system_g.api_client import get_api_client
from src.system_g.strategy import MovingAverageCrossover


if __name__ == "__main__":
    # ==========================================================================
    # INITIALIZATION SEQUENCE
    # ==========================================================================
    try:
        # Set up logger first so all subsequent actions can be logged
        logger = setup_logger(config.LOG_FILE)
        logger.info("--- System-G P0-Validator Starting ---")
        
        # Get the appropriate API client based on MODE
        api_client = get_api_client(config)
        
        # Instantiate the strategy with dependencies
        strategy = MovingAverageCrossover(
            api_client=api_client,
            instrument_token=config.INSTRUMENT_TOKEN,
            short_window=config.SHORT_WINDOW,
            long_window=config.LONG_WINDOW
        )
        
        logger.info("All components initialized successfully.")
        logger.info(f"MODE: {config.MODE} | Token: {config.INSTRUMENT_TOKEN} | Qty: {config.QUANTITY}")
        logger.info(f"Loop frequency: {config.LOOP_FREQUENCY_SECONDS}s")
        
    except Exception as e:
        print(f"FATAL: Initialization failed - {e}")
        raise SystemExit(1)
    
    # ==========================================================================
    # MAIN CONTROL LOOP
    # ==========================================================================
    while True:
        try:
            # Get trading signal from strategy
            signal = strategy.get_signal()
            logger.info(f"Signal received: {signal}")
            
            # Get current position
            position_qty = api_client.get_open_position_qty(config.INSTRUMENT_TOKEN)
            logger.info(f"Current position: {position_qty}")
            
            # Decision Matrix
            if signal == "BUY" and position_qty == 0:
                logger.info(f"ACTION: Opening position - BUY {config.QUANTITY} units")
                api_client.submit_order(config.INSTRUMENT_TOKEN, config.QUANTITY, "BUY")
                
            elif signal == "SELL" and position_qty > 0:
                logger.info(f"ACTION: Closing position - SELL {position_qty} units")
                api_client.submit_order(config.INSTRUMENT_TOKEN, position_qty, "SELL")
                
            else:
                if signal == "HOLD":
                    logger.info("NO ACTION: Signal is HOLD")
                elif signal == "BUY" and position_qty > 0:
                    logger.info("NO ACTION: Already in position for BUY signal")
                elif signal == "SELL" and position_qty == 0:
                    logger.info("NO ACTION: No position to sell")
                else:
                    logger.info(f"NO ACTION: Condition not met (signal={signal}, position={position_qty})")
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        
        # Loop frequency control
        time.sleep(config.LOOP_FREQUENCY_SECONDS)
