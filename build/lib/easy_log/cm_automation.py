import os
import requests
import subprocess
from config_gen import load_config
from datetime import datetime, timedelta
from bitbucket import get_commits_by_date
from ai_task_generator import generate_tasks_with_ai
from jira_task_creator import *
from custom_key_gen import *

REQUIRED_KEYS = [
    "BITBUCKET_USER",
    "BITBUCKET_APP_PASSWORD",
    "BITBUCKET_WORKSPACE",
    "DISPLAY_NAME",
    "JIRA_URL",
    "JIRA_API_TOKEN",
    "JIRA_USER_EMAIL",
    "GEMINI_API_KEY"
]

def select_projects(today_commits):
    """Allow user to select multiple projects."""
    print("Available projects with commits:")
    for i, repo in enumerate(today_commits.keys(), 1):
        print(f"{i}. {repo}")
    
    selected_projects = input("Select projects by numbers (comma-separated): ").strip()
    selected_project_numbers = selected_projects.split(",")

    selected_repos = []
    for number in selected_project_numbers:
        try:
            selected_repo = list(today_commits.keys())[int(number) - 1]
            selected_repos.append(selected_repo)
        except (ValueError, IndexError):
            print(f"Invalid project number: {number}. Skipping.")
    
    return selected_repos
    
    


def select_date():
    """Allow user to select the date for commits."""
    print("Select a date option:")
    print("1. Today")
    print("2. Yesterday")
    print("3. Custom Date")

    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        return datetime.utcnow().strftime("%Y-%m-%d")
    elif choice == "2":
        yesterday = datetime.utcnow() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    elif choice == "3":
        custom_date = input("Enter the custom date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(custom_date, "%Y-%m-%d")  # Validate the date format
            return custom_date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return select_date()
    else:
        print("Invalid selection. Try again.")
        return select_date()


def save_config(config):
    """Save the configuration to the file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def setup_config():
    """Prompt the user to set up the configuration."""
    print("\nConfiguration setup is required. Please provide the following details:")
    config = {}
    for key in REQUIRED_KEYS:
        value = input(f"Enter {key}: ").strip()
        while not value:
            print(f"{key} cannot be empty. Please try again.")
            value = input(f"Enter {key}: ").strip()
        config[key] = value
    save_config(config)
    print("Configuration saved successfully.")


def validate_config(config):
    """Validate if all required keys are present and non-empty."""
    missing_keys = [key for key in REQUIRED_KEYS if not config.get(key)]
    return missing_keys

def ensure_config():
    """Ensure the configuration is valid before proceeding."""
    config = load_config()
    missing_keys = validate_config(config)
    if missing_keys:
        print("The following configuration values are missing or empty:")
        for key in missing_keys:
            print(f"- {key}")
        setup_config()
        config = load_config()  # Reload the updated configuration
    return config


def gen_key(JIRA_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL):
    """
    Generate a key by setting up a Jira project, issue types, and dropdown configurations.
    """
    # Prompt the user to enter the Jira Project Key
    project_key = input("Enter Jira Project Key for setup: ").strip()

    # Check if the project already exists in the configuration
    project_exist = add_project(project_key)

    # If the project already exists, exit the function early
    if project_exist:
        print("Project setup aborted as the project already exists.")
        return

    # Initialize an empty list to store the selected issue types
    issue_types = []

    # Loop until the user provides a valid input for issue type selection
    while True:
        # Prompt the user to select an issue type using numbers
        issue_type_input = input(
            "Enter issue type to configure (1 for Task, 2 for Bug, 3 for Both): "
        ).strip()

        # Map the numeric input to the corresponding issue type
        if issue_type_input == "1":
            issue_types = ["Task"]
            break
        elif issue_type_input == "2":
            issue_types = ["Bug"]
            break
        elif issue_type_input == "3":
            issue_types = ["Task", "Bug"]
            break
        else:
            print("Invalid input. Please enter '1' for Task, '2' for Bug, or '3' for Both.")

    # Iterate over the selected issue types and process each one
    for issue_type in issue_types:
        print(f"\n🚀 Attempting to create a {issue_type} in Jira...")

        # Attempt to create a Jira task/bug
        create_jira_key(project_key, issue_type, JIRA_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL)

        # Ask the user if they want to set dropdown values for the current issue type
        set_dropdown = input(f"Do you want to set dropdown values for {issue_type}? (Y/N): ").strip().upper()
        if set_dropdown == "Y":
            create_jira_task_or_issue_key(project_key, issue_type, JIRA_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL)
            
def add_project(project_name):
    """Add a project to the configuration."""
    # Load the current configuration
    config = load_config()

    # Ensure the 'projects' key exists
    if 'projects' not in config:
        config['projects'] = []

    # Add the project if it's not already in the list
    if project_name not in config['projects']:
        config['projects'].append(project_name)
        # Save the updated configuration
        save_config(config)
        print(f"Project '{project_name}' added successfully.")
        return False
    else:
        print(f"Project '{project_name}' already exists in the list.")
        return True
   

def main():
    # Ensure configuration is valid before proceeding
    config = ensure_config()
    
    BITBUCKET_USER = config.get("BITBUCKET_USER")
    BITBUCKET_APP_PASSWORD = config.get("BITBUCKET_APP_PASSWORD")
    BITBUCKET_WORKSPACE = config.get("BITBUCKET_WORKSPACE")
    DISPLAY_NAME = config.get("DISPLAY_NAME")
    # 🔹 Jira Credentials & Base URL
    JIRA_URL = config.get("JIRA_URL")
    JIRA_API_TOKEN = config.get("JIRA_API_TOKEN")
    JIRA_USER_EMAIL = config.get("JIRA_USER_EMAIL")
   
  
    gen_key(JIRA_URL,JIRA_API_TOKEN,JIRA_USER_EMAIL)
    
    # Proceed with the main logic
    print("Select date to fetch commits:")
    selected_date = select_date()
    print(f"Fetching repositories with commits from {selected_date}...")
    today_commits = get_commits_by_date(
            selected_date,
            BITBUCKET_USER,
            BITBUCKET_APP_PASSWORD,
            BITBUCKET_WORKSPACE,
            DISPLAY_NAME
    )
    
    if not today_commits:
        print(f"No repositories have your commits on {selected_date}.")
        return
    
    selected_repos = select_projects(today_commits)
    if not selected_repos:
        print("No projects selected. Exiting.")
        return
    
    # Gather all commit messages from the selected repositories
    combined_commit_messages = []
    for selected_repo in selected_repos:
        print(f"\nProcessing repository: {selected_repo}")
        combined_commit_messages.extend(today_commits[selected_repo])
    
    # Join all commit messages into a single string
    all_commit_messages = "\n".join(combined_commit_messages)
    
    num_tasks = int(input("Enter the number of tasks to generate: ").strip())
    
    # Ask for AI model selection
    print("Select AI model for task generation:")
    print("1. Gemini")
    print("2. DeepSeek")
    print("3. OpenAI")
    
    model_choice = input("Enter choice (1/2/3): ").strip()
    
    model_map = {"1": "gemini", "2": "deepseek", "3": "openai"}
    selected_model = model_map.get(model_choice)
    if not selected_model:
        print("Invalid selection. Skipping task generation.")
        return
    
    print(f"Generating tasks with {selected_model}...")
    tasks = generate_tasks_with_ai(all_commit_messages, selected_model, num_tasks)
    
    # Process each generated task
    for i, task in enumerate(tasks):
        print(f"\nGenerated Task {i+1}: {task}")
        
        # Prompt for issue type for each task
        while True:
            issue_type_input = input("Enter issue type (1 for Task, 2 for Bug): ").strip()
            if issue_type_input == "1":
                issue_type = "Task"
                break
            elif issue_type_input == "2":
                issue_type = "Bug"
                break
            else:
                print("Invalid input. Please enter '1' for Task or '2' for Bug.")
        
        # Prompt for Jira project key
        project_key = input("Enter project key for Jira Task : ").strip().upper()
        
        # Prompt for time estimate
        time_estimate = select_time_estimate()
        
        # Get user-selected task category and task size
        selected_task_category_keys = get_user_selected_task_category(project_key, issue_type)
        selected_task_size_keys = get_user_selected_task_size(project_key, issue_type)
        
        # Create the Jira task/bug
        if project_key:
            issue_key = create_jira_task_or_issue(
                project_key,
                issue_type,
                task,
                "Generated from AI commit analysis",
                selected_task_category_keys,
                selected_task_size_keys,
                selected_date,
                time_estimate
            )
            if issue_key:
                print(f"✔ Created {issue_type}: {issue_key} in project {project_key}")

if __name__ == "__main__":
    main()
