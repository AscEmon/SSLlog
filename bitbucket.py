import requests
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    

    
    
BITBUCKET_USER =config['BITBUCKET_USER']
BITBUCKET_APP_PASSWORD = config['BITBUCKET_APP_PASSWORD']
BITBUCKET_WORKSPACE = config['BITBUCKET_WORKSPACE']
DISPLAY_NAME = config['DISPLAY_NAME']
#"Abu sayed"
#"AscEmon"


def get_commits_by_date(date):
    """Fetch commits for the given date and filter by the current user."""
    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
    headers = {"Accept": "application/json"}
    commits_by_date = {}

    while url:
        response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_APP_PASSWORD), headers=headers)

        if response.status_code != 200:
            print("Error fetching repositories:", response.text)
            return {}

        data = response.json()

        for repo in data.get("values", []):
            repo_slug = repo["slug"]
            commit_url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{repo_slug}/commits"

            commit_response = requests.get(commit_url, auth=(BITBUCKET_USER, BITBUCKET_APP_PASSWORD), headers=headers)

            if commit_response.status_code == 200:
                commits = commit_response.json().get("values", [])
                for commit in commits:
                    commit_date = commit["date"][:10]  # Extract YYYY-MM-DD
                    
                    # Normalize the input date to the same format (YYYY-MM-DD)
                    if commit_date == date:
                        author = commit.get("author", {})
                        user = author.get("user", {})

                        if user and "display_name" in user:
                            if user["display_name"] == DISPLAY_NAME:
                                if repo_slug not in commits_by_date:
                                    commits_by_date[repo_slug] = []
                                commits_by_date[repo_slug].append(commit["message"])
                                break  # No need to check more commits in this repo
                        elif "email" in author:  # Handle email-based author
                            if author["email"] == BITBUCKET_USER:
                                if repo_slug not in commits_by_date:
                                    commits_by_date[repo_slug] = []
                                commits_by_date[repo_slug].append(commit["message"])
                                break  # No need to check more commits in this repo

        url = data.get("next")  # Handle pagination

    return commits_by_date
