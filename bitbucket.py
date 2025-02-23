#import requests
#import json
#
#with open('config.json', 'r') as config_file:
#    config = json.load(config_file)
#    
#
#    
#    
#BITBUCKET_USER =config['BITBUCKET_USER']
#BITBUCKET_APP_PASSWORD = config['BITBUCKET_APP_PASSWORD']
#BITBUCKET_WORKSPACE = config['BITBUCKET_WORKSPACE']
#DISPLAY_NAME = config['DISPLAY_NAME']
##"Abu sayed"
##"AscEmon"
#
#
#def get_commits_by_date(date):
#    """Fetch commits for the given date and filter by the current user."""
#    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
#    headers = {"Accept": "application/json"}
#    commits_by_date = {}
#
#    while url:
#        response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_APP_PASSWORD), headers=headers)
#
#        if response.status_code != 200:
#            print("Error fetching repositories:", response.text)
#            return {}
#
#        data = response.json()
#
#        for repo in data.get("values", []):
#            repo_slug = repo["slug"]
#            commit_url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{repo_slug}/commits"
#
#            commit_response = requests.get(commit_url, auth=(BITBUCKET_USER, BITBUCKET_APP_PASSWORD), headers=headers)
#
#            if commit_response.status_code == 200:
#                commits = commit_response.json().get("values", [])
#                for commit in commits:
#                    commit_date = commit["date"][:10]  # Extract YYYY-MM-DD
#                    
#                    # Normalize the input date to the same format (YYYY-MM-DD)
#                    if commit_date == date:
#                        author = commit.get("author", {})
#                        user = author.get("user", {})
#
#                        if user and "display_name" in user:
#                            if user["display_name"] == DISPLAY_NAME:
#                                if repo_slug not in commits_by_date:
#                                    commits_by_date[repo_slug] = []
#                                commits_by_date[repo_slug].append(commit["message"])
#                                break  # No need to check more commits in this repo
#                        elif "email" in author:  # Handle email-based author
#                            if author["email"] == BITBUCKET_USER:
#                                if repo_slug not in commits_by_date:
#                                    commits_by_date[repo_slug] = []
#                                commits_by_date[repo_slug].append(commit["message"])
#                                break  # No need to check more commits in this repo
#
#        url = data.get("next")  # Handle pagination
#
#    return commits_by_date



import requests
import json
from pathlib import Path

# Define the path to the configuration file
CONFIG_FILE = Path("config.json")

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

#def main():
#    try:
#        # Load configuration
#        config = load_config()
#        
#        # Extract configuration values
#        BITBUCKET_USER = config.get("BITBUCKET_USER")
#        BITBUCKET_APP_PASSWORD = config.get("BITBUCKET_APP_PASSWORD")
#        BITBUCKET_WORKSPACE = config.get("BITBUCKET_WORKSPACE")
#        DISPLAY_NAME = config.get("DISPLAY_NAME")
#        
#        # Validate configuration
#        if not all([BITBUCKET_USER, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE, DISPLAY_NAME]):
#            raise ValueError("One or more required configuration values are missing.")
#        
#        # Prompt user for date
#        selected_date = input("Enter date to fetch commits (YYYY-MM-DD): ").strip()
#        
#        # Fetch commits for the selected date
#        print(f"Fetching repositories with commits from {selected_date}...")
#        today_commits = get_commits_by_date(
#            selected_date,
#            BITBUCKET_USER,
#            BITBUCKET_APP_PASSWORD,
#            BITBUCKET_WORKSPACE,
#            DISPLAY_NAME
#        )
#        
#        if not today_commits:
#            print(f"No repositories have your commits on {selected_date}.")
#            return
#        
#        # Display the fetched commits
#        print("\nRepositories with commits:")
#        for repo, commits in today_commits.items():
#            print(f"\nRepository: {repo}")
#            print("Commits:")
#            for commit in commits:
#                print(f"- {commit}")
#    
#    except Exception as e:
#        print(f"An error occurred: {e}")
#
#if __name__ == "__main__":
#    main()
