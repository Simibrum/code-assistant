"""File that runs the agent."""
import argparse
import agent.core as core

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate_tests", action="store_true")
    parser.add_argument("--generate_module_docstrings", action="store_true")
    parser.add_argument("--format_modules", action="store_true")
    parser.add_argument("--run_task", action="store_true")
    args = parser.parse_args()

    if args.generate_tests:
        core.generate_tests()

    if args.generate_module_docstrings:
        core.generate_module_docstrings()

    if args.format_modules:
        core.format_modules()

    if args.run_task:
        core.run_task()
