import requests
import json
from datetime import datetime
import os

# Path to the configuration file
CONFIG_FILE =  os.path.expanduser("~/.easy_log/config.json")

def load_config():
    """Load existing config.json."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILE}' not found.")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_jira_auth():
    """Extract Jira authentication details from the configuration."""
    config = load_config()
    JIRA_URL = config.get("JIRA_URL")
    JIRA_API_TOKEN = config.get("JIRA_API_TOKEN")
    JIRA_USER_EMAIL = config.get("JIRA_USER_EMAIL")
    
    if not all([JIRA_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL]):
        raise ValueError("One or more required Jira configuration values are missing in 'config.json'.")
    
    return {
        "url": JIRA_URL,
        "auth": (JIRA_USER_EMAIL, JIRA_API_TOKEN),
        "headers": {
            "Content-Type": "application/json",
            "Authorization": f"Basic {requests.auth._basic_auth_str(JIRA_USER_EMAIL, JIRA_API_TOKEN)}"
        }
    }

def get_user_selected_task_category(project_key, issue_type):
    """Get the user-selected Task Category ID based on the configuration."""
    config = load_config()
    # Get the Task Category section for the specified project key and issue type
    task_category_config = config.get(project_key, {}).get(issue_type, {}).get("Task Category", {})
    if not task_category_config:
        print(f"❌ No Task Category configuration found for project '{project_key}' and issue type '{issue_type}'.")
        return None
    
    # Filter out the "field_key" entry and build the task_categories dictionary
    filtered_categories = {
        category_name: category_id
        for category_name, category_id in task_category_config.items()
        if category_name != "field_key"
    }
    
    # Dynamically build the task_categories dictionary with proper numbering
    task_categories = {
        str(idx): (category_name, category_id)
        for idx, (category_name, category_id) in enumerate(filtered_categories.items(), start=1)
    }
    
    # Display the task categories to the user
    while True:
        print("\nSelect Task Category:")
        for key, (value, _) in task_categories.items():
            print(f"{key}. {value}")
        
        # Get the user's choice
        user_choice = input("Enter the number corresponding to your choice: ").strip()
        
        # Validate selection
        if user_choice in task_categories:
            selected_category_id = task_categories[user_choice][1]
            print(f"✅ Selected Task Category: {task_categories[user_choice][0]}")
            return selected_category_id
        else:
            print("❌ Invalid choice! Please enter a valid number.")


def get_user_selected_task_size(project_key, issue_type):
    """Get the user-selected Task Size ID based on the configuration."""
    config = load_config()
    # Get the Task Size section for the specified project key and issue type
    task_size_config = config.get(project_key, {}).get(issue_type, {}).get("Task Size", {})
    if not task_size_config:
        print(f"❌ No Task Size configuration found for project '{project_key}' and issue type '{issue_type}'.")
        return None
    
    # Filter out the "field_key" entry and build the task_sizes dictionary
    filtered_sizes = {
        size_name: size_id
        for size_name, size_id in task_size_config.items()
        if size_name != "field_key"
    }
    
    # Dynamically build the task_sizes dictionary with proper numbering
    task_sizes = {
        str(idx): (size_name, size_id)
        for idx, (size_name, size_id) in enumerate(filtered_sizes.items(), start=1)
    }
    
    # Display the task sizes to the user
    while True:
        print("\nSelect Task Size:")
        for key, (value, _) in task_sizes.items():
            print(f"{key}. {value}")
        
        # Get the user's choice
        user_choice = input("Enter the number corresponding to your choice: ").strip()
        
        # Validate selection
        if user_choice in task_sizes:
            selected_size_id = task_sizes[user_choice][1]
            print(f"✅ Selected Task Size: {task_sizes[user_choice][0]}")
            return selected_size_id
        else:
            print("❌ Invalid choice! Please enter a valid number.")

def create_jira_task_or_issue(PROJECT_KEY, issue_type, task, description, selected_task_category_keys, selected_task_size_keys, selected_date, time_estimate="2h"):
    """Create a Jira task or issue dynamically with custom fields loaded from config.json."""
    jira_auth = get_jira_auth()
    JIRA_URL = jira_auth["url"]
    auth = jira_auth["auth"]
    config = load_config()
    # Retrieve custom field mappings for the given PROJECT_KEY
    custom_fields = config.get(PROJECT_KEY, {}).get(issue_type, {})
    if not custom_fields:
        print(f"⚠️ Error: Project '{PROJECT_KEY}' or issue type '{issue_type}' not found in config.json")
        return
    
    # Build the Jira request payload dynamically, based on custom fields
    url = f"{JIRA_URL}/rest/api/3/issue"
    summary = task
    formatted_due_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime('%Y-%m-%d')
    
    data = {
        "fields": {
            "project": {"key": PROJECT_KEY},  # Project Key
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"text": description, "type": "text"}]}]
            },
            "issuetype": {"name": issue_type},  # Task or Bug
        }
    }
    
    # Dynamically add custom fields to the payload
    for field_name, field_config in custom_fields.items():
#        print(f"Processing custom field: {field_name}, Config: {field_config}")
        
        # Extract the field key based on its type
        if isinstance(field_config, dict) and "field_key" in field_config:
            field_key = field_config["field_key"]  # Nested field_key for Task Size and Task Category
        elif isinstance(field_config, str):
            field_key = field_config  # Direct string for other fields
        else:
            print(f"⚠️ Invalid configuration for '{field_name}'. Skipping this field.")
            continue
        
        # Add the field to the payload based on its name
        if field_name == "Task Size":
            data["fields"][field_key] = {"id": selected_task_size_keys}
        elif field_name == "Orginal Estimate":
            data["fields"][field_key] = time_estimate
        elif field_name == "Task Category":
            data["fields"][field_key] = {"id": selected_task_category_keys}
        elif field_name in ["Start Date", "End Date"]:
            data["fields"][field_key] = formatted_due_date
    
#    print(f"Payload for Jira API: {data}")
    
    response = requests.post(url, json=data, auth=auth, headers={"Content-Type": "application/json"})
    
    if response.status_code == 201:
        issue_key = response.json()["key"]
        log_task_in_jira(issue_key, PROJECT_KEY, summary, issue_type, time_estimate)
        print(f"✅ Successfully created {issue_type}: {issue_key}")
    else:
        print(f"❌ Failed to create {issue_type}: {response.text}")


def log_task_in_jira(issue_key, PROJECT_KEY, summary, issue_type, time_estimate, new_status="Done"):
    """Log task creation details in Jira and optionally update the issue status."""
    jira_auth = get_jira_auth()
    JIRA_URL = jira_auth["url"]
    auth = jira_auth["auth"]
    
    # Step 1: Log work in Jira
    work_log_payload = {
        "timeSpent": time_estimate,  # e.g., "2h" or "30m"
        "started": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),  # UTC timestamp
        "comment": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": summary
                        }
                    ]
                }
            ]
        }
    }
    
    # Call the Work Log API
    work_log_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/worklog"
    work_log_response = requests.post(work_log_url, json=work_log_payload, auth=auth, headers={"Content-Type": "application/json"})
    
    if work_log_response.status_code == 201:
        print(f"✅ Logged task creation details in Jira issue: {issue_key} for {PROJECT_KEY}")
    else:
        print(f"❌ Failed to log task creation details in Jira: {work_log_response.text}")
        return  # Stop further execution if work logging fails
    
    # Step 2: Update the issue status (if a new status is provided)
    if new_status:
        # Get the list of available transitions for the issue
        transitions_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
        transitions_response = requests.get(transitions_url, auth=auth, headers={"Content-Type": "application/json"})
        
        if transitions_response.status_code != 200:
            print(f"❌ Failed to fetch transitions for issue {issue_key}: {transitions_response.text}")
            return
        
        # Parse the available transitions
        transitions = transitions_response.json().get("transitions", [])
        transition_id = None
        
        # Find the transition ID corresponding to the desired status
        for transition in transitions:
            if transition["name"].lower() == new_status.lower():
                transition_id = transition["id"]
                break
        
        if not transition_id:
            print(f"❌ No transition found for status '{new_status}' in issue {issue_key}.")
            return
        
        # Perform the transition
        transition_payload = {
            "transition": {
                "id": transition_id
            }
        }
        transition_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
        transition_response = requests.post(transition_url, json=transition_payload, auth=auth, headers={"Content-Type": "application/json"})
        
        if transition_response.status_code == 204:
            print(f"✅ Updated issue {issue_key} status to '{new_status}'.")
        else:
            print(f"❌ Failed to update issue {issue_key} status to '{new_status}': {transition_response.text}")

def select_jira_project_for_repo(selected_repos):
    """Map selected Bitbucket repositories to Jira projects."""
    repo_to_jira = {}
    for repo in selected_repos:
        jira_project = input(f"Enter Jira project key for repository '{repo}': ").strip().upper()
        repo_to_jira[repo] = jira_project
    return repo_to_jira

def select_task_or_issue():
    """Ask the user if they want to create a task or an issue."""
    print("Select issue type:")
    print("1. Task")
    print("2. Bug")
    choice = input("Enter choice (1/2): ").strip()
    return "Task" if choice == "1" else "Bug"

def select_time_estimate():
    """Allow user to enter the estimated time (default: 2 hours)."""
    time_estimate = input("Enter time estimate (default: 2h, e.g., '3h 30m'): ").strip()
    return time_estimate if time_estimate else "2h"
