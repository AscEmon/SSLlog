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

# Path to the configuration file
CONFIG_FILE = Path("config.json")

def load_config():
    """Load the configuration file."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_config(config):
    """Save the configuration to the file."""
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

#def main():
#    # Load the existing configuration
#    config = load_config()
#
#    # Validate the configuration
#    missing_keys = validate_config(config)
#    if missing_keys:
#        print("The following configuration values are missing or empty:")
#        for key in missing_keys:
#            print(f"- {key}")
#        setup_config()
#        config = load_config()  # Reload the updated configuration
#
#    # Proceed to the next step
#    print("Configuration is complete. Proceeding to the next step...")
#    # Your logic for the next step goes here
#
#if __name__ == "__main__":
#    main()
