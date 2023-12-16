"""Package for agent functions."""


class BaseAgent:
    """Abstract class for all agents."""

    name: str = "BaseAgent"

    def loop(self):
        """Run the agent's loop."""
        raise NotImplementedError("This agent does not have a loop.")
