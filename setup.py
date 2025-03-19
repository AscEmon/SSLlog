import os
import json
from setuptools import setup, find_packages

# Define the default configuration file path
CONFIG_FILE = os.path.expanduser("~/.ssl_log/config.json")

# Ensure the config directory exists and create an empty config file if it doesn't
def create_default_config():
    """Create an empty configuration file if it doesn't exist."""
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)  # Create the directory if it doesn't exist

    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "BITBUCKET_USER": "",
            "BITBUCKET_APP_PASSWORD": "",
            "BITBUCKET_WORKSPACE": "",
            "DISPLAY_NAME": "",
            "JIRA_URL": "",
            "JIRA_API_TOKEN": "",
            "JIRA_USER_EMAIL": "",
            "GEMINI_API_KEY": ""
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(default_config, file, indent=4)
        print(f"Created default configuration file at: {CONFIG_FILE}")
    else:
        print("Configuration file already exists.")

# Call the function during installation
create_default_config()

setup(
    name="ssl_log",
    version="1.0.1",
    author="Abu Sayed Chowdhury",
    author_email="sayem227@gmail.com",
    description="A CLI tool to automate logging tasks from Bitbucket to Jira.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AscEmon/SSLlog",  # Optional: Link to your repository
    packages=find_packages(),
    install_requires=[
        "requests",  # Add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "ssl_log=ssl_log.cli:cli",  # This makes `easy_log` available as a command
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
