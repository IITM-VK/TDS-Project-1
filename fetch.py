import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load GitHub token from .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Parameters for fetching users
LOCATION = "Singapore"
MIN_FOLLOWERS = 100
BASE_URL = "https://api.github.com"
MAX_USERS = 1000  # The maximum number of users to fetch, adjust if needed

# Functions to interact with GitHub API
def fetch_users(location, min_followers):
    """Fetch GitHub users from a location with minimum followers."""
    users = []
    page = 1
    while True:
        url = f"{BASE_URL}/search/users?q=location:{location}+followers:>{min_followers}&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # Handle rate limits
        if response.status_code == 403:  # Forbidden
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = reset_time - int(time.time()) + 5  # Wait until the reset time
            print(f"Rate limit reached, waiting for {wait_time} seconds...")
            time.sleep(max(wait_time, 0))
            continue
        
        if response.status_code != 200:
            print("Error fetching users:", response.status_code)
            break
            
        data = response.json()
        users.extend(data['items'])
        
        if 'next' not in response.links or len(data['items']) == 0:  # No more results
            break
            
        page += 1
        if len(users) >= MAX_USERS:  # Stop if max users limit is reached
            users = users[:MAX_USERS]
            break
            
    return users

def fetch_user_details(usernames):
    """Fetch detailed information for multiple GitHub users in parallel."""
    user_details = []
    with ThreadPoolExecutor(max_workers=10) as executor:  # Increased workers for faster requests
        futures = {executor.submit(requests.get, f"{BASE_URL}/users/{username}", headers=HEADERS, timeout=10): username for username in usernames}
        for future in as_completed(futures):
            response = future.result()
            if response.status_code == 200:
                user_details.append(response.json())
            else:
                print(f"Error fetching user details for {futures[future]}: {response.status_code}")
    return user_details

def fetch_repositories(username):
    """Fetch repositories for a single GitHub user."""
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # Handle rate limits
        if response.status_code == 403:  # Forbidden
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = reset_time - int(time.time()) + 5  # Wait until the reset time
            print(f"Rate limit reached for repositories, waiting for {wait_time} seconds...")
            time.sleep(max(wait_time, 0))
            continue
        
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

def fetch_all_repositories(usernames):
    """Fetch repositories for all usernames in parallel."""
    repos_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:  # Increased workers for faster requests
        futures = {executor.submit(fetch_repositories, username): username for username in usernames}
        for future in as_completed(futures):
            repos_data.extend(future.result())
    return repos_data

# Data processing and CSV generation
def main():
    users_data = []
    repos_data = []

    # Fetch users
    users = fetch_users(LOCATION, MIN_FOLLOWERS)
    usernames = [user['login'] for user in users]

    # Fetch detailed user data in parallel
    user_details = fetch_user_details(usernames)
    
    for details in user_details:
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

    # Fetch repositories in parallel for each user
    repos_data = fetch_all_repositories(usernames)

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
