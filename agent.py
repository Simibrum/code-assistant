"""
This is the main script that uses all the other components to perform tasks. 
It would contain the main loop of the agent, where it determines the next task, 
performs the task, evaluates the result, and repeats.
"""
from utils import extract_project_description

description = extract_project_description('README.md')
print(description)
