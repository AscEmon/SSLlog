import os
import json
from pathlib import Path

# Define the required configuration keys
REQUIRED_KEYS = [
    "BITBUCKET_USER",
    "BITBUCKET_APP_PASSWORD",
    "BITBUCKET_WORKSPACE",
    "DISPLAY_NAME",
    "JIRA_URL",
    "JIRA_API_TOKEN",
    "JIRA_USER_EMAIL"
]

# Define the config file path
CONFIG_FILE = os.path.expanduser("~/.easy_log/config.json")

def load_config():
    """Load the configuration from the file."""
    if not os.path.exists(CONFIG_FILE):
        return {}  # Return an empty dictionary if the file doesn't exist

    with open(CONFIG_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Error: The configuration file is not valid JSON.")
            return {}

def save_config(config):
    """Save the configuration to the file."""
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)  # Create the directory if it doesn't exist

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
        
        
def validate_config(config):
    """Validate if all required keys are present and non-empty."""
    missing_keys = [key for key in REQUIRED_KEYS if not config.get(key)]
    return missing_keys

def setup_config():
    """Prompt the user to set up the configuration."""
    print("Configuration setup is required. Please provide the following details:")
    config = {}
    for key in REQUIRED_KEYS:
        value = input(f"Enter {key}: ").strip()
        while not value:
            print(f"{key} cannot be empty. Please try again.")
            value = input(f"Enter {key}: ").strip()
        config[key] = value
    save_config(config)
    print("Configuration saved successfully.")

