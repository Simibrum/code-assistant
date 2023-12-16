"""An agent class for managing the project. Does not code."""
from agent import BaseAgent
from functions import logger


class ProjectManager(BaseAgent):
    """An agent class for managing the project. Does not code."""

    name = "ProjectManager"

    def loop(self):
        """Run the agent's loop."""
        logger.info("I'm managing the project.")
