import os
import requests
import subprocess
from datetime import datetime, timedelta
from bitbucket import get_commits_by_date
from ai_task_generator import generate_tasks_with_ai
from jira_task_creator import *


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


def main():
    print("Select date to fetch commits:")
    selected_date = select_date()
    print(f"Fetching repositories with commits from {selected_date}...")
    today_commits = get_commits_by_date(selected_date)
    
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
        project_key = input("Enter Jira project key for which you are selecting task size: ").strip().upper()
        
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
