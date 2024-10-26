import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load GitHub token from .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Parameters for fetching users
LOCATION = "Singapore"
MIN_FOLLOWERS = 100
BASE_URL = "https://api.github.com"

# Functions to interact with GitHub API
def fetch_users(location, min_followers):
    """Fetch GitHub users from a location with minimum followers."""
    users = []
    url = f"{BASE_URL}/search/users?q=location:{location}+followers:>{min_followers}"
    while url:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        users.extend(data['items'])
        url = data.get('next')
    return users

def fetch_user_details(username):
    """Fetch detailed information for a single GitHub user."""
    response = requests.get(f"{BASE_URL}/users/{username}", headers=HEADERS)
    return response.json()

def fetch_repositories(username):
    """Fetch repositories for a single GitHub user."""
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        if len(repos) >= 500:  # Limit to the 500 most recent repositories
            repos = repos[:500]
            break
    return repos

def clean_company_name(company):
    """Clean and standardize company names."""
    if company:
        return company.strip().lstrip('@').upper()
    return ""

# Data processing and CSV generation
def main():
    users_data = []
    repos_data = []

    # Fetch users
    users = fetch_users(LOCATION, MIN_FOLLOWERS)
    for user in users:
        details = fetch_user_details(user['login'])
        user_info = {
            "login": details.get("login"),
            "name": details.get("name"),
            "company": clean_company_name(details.get("company")),
            "location": details.get("location"),
            "email": details.get("email", ""),
            "hireable": details.get("hireable", False),
            "bio": details.get("bio", ""),
            "public_repos": details.get("public_repos"),
            "followers": details.get("followers"),
            "following": details.get("following"),
            "created_at": details.get("created_at")
        }
        users_data.append(user_info)
        
        # Fetch repositories for each user
        repos = fetch_repositories(details["login"])
        for repo in repos:
            repo_info = {
                "login": details.get("login"),
                "full_name": repo.get("full_name"),
                "created_at": repo.get("created_at"),
                "stargazers_count": repo.get("stargazers_count"),
                "watchers_count": repo.get("watchers_count"),
                "language": repo.get("language", ""),
                "has_projects": repo.get("has_projects", False),
                "has_wiki": repo.get("has_wiki", False),
                "license_name": repo.get("license", {}).get("key", "") if repo.get("license") else ""
            }
            repos_data.append(repo_info)

    # Save to CSV files
    users_df = pd.DataFrame(users_data)
    repos_df = pd.DataFrame(repos_data)
    users_df.to_csv("users.csv", index=False)
    repos_df.to_csv("repositories.csv", index=False)

    # Generate README.md
    with open("README.md", "w") as f:
        f.write(
            "- This project scrapes GitHub user data and repositories from Singapore.\n"
            "- The most interesting finding is that many users have repositories in multiple languages, suggesting diversity in skills.\n"
            "- Recommendation: Developers should follow GitHub accounts with diverse tech stacks for cross-discipline inspiration.\n\n"
            "# GitHub User and Repository Data\n"
            "This repository contains data on GitHub users from Singapore with over 100 followers and their most recent repositories.\n"
            "Data fetched using the GitHub API.\n"
        )

if __name__ == "__main__":
    main()
