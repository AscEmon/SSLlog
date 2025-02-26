import requests
import json
from pathlib import Path
import os
# Define the path to the configuration file
CONFIG_FILE = os.path.expanduser("~/.easy_log/config.json")

def load_config():
    """Load the configuration file."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("Configuration file 'config.json' not found.")
    with open(CONFIG_FILE, "r") as config_file:
        return json.load(config_file)

def get_commits_by_date(date, bitbucket_user, bitbucket_app_password, bitbucket_workspace, display_name):
    """
    Fetch commits for the given date and filter by the current user.
    
    Args:
        date (str): The date to fetch commits for (YYYY-MM-DD).
        bitbucket_user (str): Bitbucket username.
        bitbucket_app_password (str): Bitbucket app password.
        bitbucket_workspace (str): Bitbucket workspace name.
        display_name (str): Display name of the user.
    
    Returns:
        dict: A dictionary where keys are repository slugs and values are lists of commit messages.
    """
    url = f"https://api.bitbucket.org/2.0/repositories/{bitbucket_workspace}"
    headers = {"Accept": "application/json"}
    commits_by_date = {}
    
    while url:
        response = requests.get(url, auth=(bitbucket_user, bitbucket_app_password), headers=headers)
        if response.status_code != 200:
            print("Error fetching repositories:", response.text)
            return {}
        
        data = response.json()
        for repo in data.get("values", []):
            repo_slug = repo["slug"]
            commit_url = f"https://api.bitbucket.org/2.0/repositories/{bitbucket_workspace}/{repo_slug}/commits"
            commit_response = requests.get(commit_url, auth=(bitbucket_user, bitbucket_app_password), headers=headers)
            
            if commit_response.status_code == 200:
                commits = commit_response.json().get("values", [])
                for commit in commits:
                    commit_date = commit["date"][:10]  # Extract YYYY-MM-DD
                    
                    # Normalize the input date to the same format (YYYY-MM-DD)
                    if commit_date == date:
                        author = commit.get("author", {})
                        user = author.get("user", {})
                        
                        if user and "display_name" in user:
                            if user["display_name"] == display_name:
                                if repo_slug not in commits_by_date:
                                    commits_by_date[repo_slug] = []
                                commits_by_date[repo_slug].append(commit["message"])
                                break  # No need to check more commits in this repo
                        elif "email" in author:  # Handle email-based author
                            if author["email"] == bitbucket_user:
                                if repo_slug not in commits_by_date:
                                    commits_by_date[repo_slug] = []
                                commits_by_date[repo_slug].append(commit["message"])
                                break  # No need to check more commits in this repo
        
        url = data.get("next")  # Handle pagination
    
    return commits_by_date
