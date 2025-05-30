# app/utils/config_loader.py
import os
import yaml
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Regex pattern to match ${ENV_VAR}
env_var_pattern = re.compile(r'\${(\w+)}')

# Replaces ${VAR} with actual env value
def replace_env_vars(value: str) -> str:
    return env_var_pattern.sub(lambda match: os.getenv(match.group(1), ""), value)

# Recursively apply env var substitution to dicts/lists/strings
def substitute_env_vars(obj):
    if isinstance(obj, dict):
        return {k: substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        return replace_env_vars(obj)
    else:
        return obj

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return substitute_env_vars(data)
