"""Skeleton code for the main loop of the agent."""
import logging
import time
import signal
from typing import Type
import argparse

from functions import logger

from agent import BaseAgent
from agent.project_manager import ProjectManager


def get_agent_class(name: str) -> Type[BaseAgent]:
    """
    Get the agent class from the class name string.

    Args:
        name (str): Name of the agent class.

    Returns:
        Type[BaseAgent]: The agent class.
    """
    agents = {
        "ProjectManager": ProjectManager,
        # Add other agents here
    }
    return agents.get(name)


def signal_handler(signum, frame):
    logger.info("Signal received, terminating agent")
    # Perform any cleanup here
    exit(0)


def main_loop(agent: BaseAgent):
    while True:
        try:
            # Main functionality of the agent goes here
            agent.loop()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        time.sleep(10)  # Sleep for 10 seconds (or appropriate interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Run an agent in the loop.")
    parser.add_argument(
        "--name", type=str, required=True, help="Name of the agent class to run"
    )
    args = parser.parse_args()

    agent_class = get_agent_class(args.name)
    if agent_class:
        agent_instance = agent_class()
        main_loop(agent_instance)
    else:
        print(f"No agent found with name: {args.name}")
