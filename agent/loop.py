"""Skeleton code for the main loop of the agent."""

import time
import signal
from functions import logger


def signal_handler(signum, frame):
    logger.info("Signal received, terminating agent")
    # Perform any cleanup here
    exit(0)


def main_loop():
    while True:
        try:
            # Main functionality of the agent goes here
            pass
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        time.sleep(10)  # Sleep for 10 seconds (or appropriate interval)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    main_loop()
