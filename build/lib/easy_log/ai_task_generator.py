import subprocess
import requests
import os
import json
CONFIG_FILE = os.path.expanduser("~/.easy_log/config.json")
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

def generate_tasks_with_ai(commit_messages, model_choice,num_tasks):
    """Generate exactly {num_tasks} distinct tasks from commit messages using AI."""
    prompt = f"""Based on the following commit messages, generate exactly {num_tasks} distinct tasks. Each task should be a short, actionable statement.Dont add any Task number or anything before jira task. Just give me meaningfull jira task.\n\nCommits:\n{commit_messages}\n\n"""

    if model_choice == "gemini":
        return generate_with_gemini(prompt)
    elif model_choice == "deepseek":
        return generate_with_deepseek(prompt)
    elif model_choice == "openai":
        return generate_with_openai(prompt)
    else:
        print("Invalid model choice.")
        return []


def generate_with_gemini(prompt):
    """Generate tasks using Gemini AI."""
    config = load_config()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": config["GEMINI_API_KEY"]}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, params=params, json=data)
    
    if response.status_code == 200:
        output = response.json()
        tasks = output.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip().split("\n")
        return [task.strip() for task in tasks if task.strip()][:4]
    
    print("Error with Gemini API:", response.text)
    return []


def generate_with_deepseek(prompt):
    """Generate tasks using DeepSeek AI."""
    if not DEEPSEEK_API_KEY:
        print("DEEPSEEK_API_KEY is not set.")
        return []

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are an assistant."}, {"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        output = response.json()
        tasks = output.get("choices", [{}])[0].get("message", {}).get("content", "").strip().split("\n")
        return [task.strip() for task in tasks if task.strip()][:4]
    
    print("Error with DeepSeek API:", response.text)
    return []


def generate_with_openai(prompt):
    """Generate tasks using OpenAI (GPT-4)."""
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY is not set.")
        return []

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": "You are an AI assistant."}, {"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        output = response.json()
        tasks = output.get("choices", [{}])[0].get("message", {}).get("content", "").strip().split("\n")
        return [task.strip() for task in tasks if task.strip()][:4]
    
    print("Error with OpenAI API:", response.text)
    return []
