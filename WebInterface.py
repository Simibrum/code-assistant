from flask import Flask 
import requests
import json
import os
import openai

from functions import load_env_vars

load_env_vars()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("No key found")

openai.api_key = api_key
MODEL = "gpt-3.5-turbo"

messages = [
            {"role": "system", "content": "You are a coding assistant in Python."},
            {"role": "user", "content": ""},
        ]

