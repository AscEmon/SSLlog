
import requests
import json
from datetime import datetime
import os


# 🔹 Config file path (where we store field mappings)
CONFIG_FILE = os.path.expanduser("~/.ssl_log/config.json")
# 🔹 Required Custom Fields
REQUIRED_FIELDS = ["Task Size", "Orginal Estimate", "Task Category", "Start Date", "End Date"]


def load_config():
    """Load existing config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or invalid, return an empty dict
            return {}
    return {}

def save_config(config):
    """Save updated config to config.json"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print("\n✅ Config file updated.")
    
def update_config_with_fields(project_key, issue_type, error_json):
    """Update the config.json with missing custom fields based on error JSON"""
    # Load the existing config
    config = load_config()
    
    # Check if there is already a project key in the config
    if project_key not in config:
        config[project_key] = {}
    if issue_type not in config[project_key]:
        config[project_key][issue_type] = {}
    
    # Loop through the required fields and check if they are missing in the error response
    for field_name in REQUIRED_FIELDS:
        for key, value in error_json.get("errors", {}).items():
            if field_name.lower() in value.lower():
                # Check if the field is "Task Size" or "Task Category"
                if field_name.lower() == "task size" or field_name.lower() == "task category":
                    config[project_key][issue_type][field_name] = {"field_key": key}
                else:
                    config[project_key][issue_type][field_name] = key
                
                print(f"✅ Added '{field_name}' with ID '{key}' to config for {issue_type}.")
                break
        
    # Save the updated config
    save_config(config)


def parse_dropdown_values(error_message):
    """Parse dropdown values from the error message"""
    options = {}
    start_index = error_message.find("are ") + len("are ")
    end_index = error_message.find(", -1")
    if start_index > 0 and end_index > 0:
        dropdown_part = error_message[start_index:end_index]
        for item in dropdown_part.split(", "):
            id_value, name = item.split("[", 1)
            name = name.rstrip("]")
            options[name] = id_value
    return options
    
def update_config_with_dropdown_values(project_key, issue_type, error_json):
    """Update the config.json with dropdown values for Task Size and Task Category"""
    # Load the existing config
    config = load_config()
    
    # Initialize the project key in the config if it doesn't exist
    if project_key not in config:
        config[project_key] = {}
    if issue_type not in config[project_key]:
        config[project_key][issue_type] = {}
    
#    print("Processing error JSON:", error_json)
    
    # Process each field in the error response
    for field_name in ["Task Size", "Task Category"]:
        for key, value in error_json.get("errors", {}).items():
            if field_name.lower() in value.lower():
                # Parse the dropdown values
                dropdown_options = parse_dropdown_values(value)
                
                # Update the config with the field ID and dropdown options
                config[project_key][issue_type][field_name] = {"field_key": key}
                config[project_key][issue_type][field_name].update(dropdown_options)
                print(f"✅ Updated '{field_name}' with dropdown options for {issue_type}.")
    
    # Save the updated config
    save_config(config)



def create_jira_key(project_key, issue_type,JIRA_URL,JIRA_API_TOKEN,JIRA_USER_EMAIL):
    """Create a Jira task and handle missing custom fields"""
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    data = {
        "fields": {
            "project": {"key": project_key},
            "summary": f"Test {issue_type} for Custom Fields",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"text": f"Testing custom fields for {issue_type}", "type": "text"}]}]
            },
            "issuetype": {"name": issue_type},
        }
    }
    url = f"{JIRA_URL}/rest/api/3/issue"
    response = requests.post(url, json=data, auth=auth, headers={"Content-Type": "application/json"})
    
    if response.status_code == 201:
        issue_key = response.json()["key"]
        print(f"✅ Successfully created {issue_type}: {issue_key}")
    else:
#        print(f"⚠️ Jira Error: {response.text}")
        
        try:
            error_json = response.json()
            if "errors" in error_json:
                print(f"\n🔎 Updating config with missing custom fields for {issue_type}...")
                update_config_with_fields(project_key, issue_type, error_json)
        except json.JSONDecodeError:
            print("❌ Failed to parse error response as JSON.")


def create_jira_task_or_issue_key(PROJECT_KEY,issue_type,JIRA_URL,JIRA_API_TOKEN,JIRA_USER_EMAIL):
    """Create a Jira task or issue dynamically with custom fields loaded from config.json."""
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    # 🔹 Load the custom field mappings from config.json
    config = load_config()

    # 🔹 Retrieve custom field mappings for the given PROJECT_KEY
    if PROJECT_KEY in config:
        custom_fields = config[PROJECT_KEY][issue_type]
    else:
        print(f"⚠️ Error: Project '{PROJECT_KEY}' not found in config.json")
        return

    url = f"{JIRA_URL}/rest/api/3/issue"

    # 🔹 Use the AI-generated task as both the summary and description
    selected_date = "2025-02-10"
    task = issue_type
    selected_task_category_keys = "selected_task_category_keys"
    selected_task_size_keys = "selected_task_size_keys"
    issue_type = issue_type
    time_estimate = "2h"
    summary = task
    description = task
    formatted_due_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime('%Y-%m-%d')
    
    # 🔹 Build the Jira request payload dynamically, based on custom fields
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
        print(f"Processing custom field: {field_name}, Config: {field_config}")
        
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
    
    print(f"Payload for Jira API: {data}")
    
    url = f"{JIRA_URL}/rest/api/3/issue"
    response = requests.post(url, json=data, auth=auth, headers={"Content-Type": "application/json"})
    
    if response.status_code == 201:
        issue_key = response.json()["key"]
        print(f"✅ Successfully created {issue_type}: {issue_key}")
    else:
        update_config_with_dropdown_values(PROJECT_KEY,issue_type, response.json())
        print(f"✅ Successfully created {issue_type} json")
   
