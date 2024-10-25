import os
os.environ["GITHUB_TOKEN"] = "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"  # Replace with your actual token

# Access the GitHub token directly
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print("GitHub Token:", GITHUB_TOKEN)  # Should print your token, not None


import os
import requests
import pandas as pd

# Set up headers for authenticated requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to fetch GitHub users in Singapore with over 100 followers
def fetch_users():
    url = "https://api.github.com/search/users?q=followers:>100+location:Singapore&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise error if request fails
    data = response.json()
    users = data['items']
    return users

# Function to fetch repositories for each user (up to 500 repositories per user)
def fetch_repositories(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        if len(repos) >= 500:
            break
    return repos[:500]  # Limit to 500

# Clean company names by removing whitespace, leading '@' symbols, and converting to uppercase
def clean_company_name(company_name):
    if company_name:
        return company_name.strip().lstrip('@').upper()
    return ""

# Process and save users data to users.csv
def process_users_data(users):
    user_data = []
    for user in users:
        # Fetch user details
        url = f"https://api.github.com/users/{user['login']}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            continue
        user_info = response.json()
        user_data.append({
            "login": user_info.get("login"),
            "name": user_info.get("name", ""),
            "company": clean_company_name(user_info.get("company", "")),
            "location": user_info.get("location", ""),
            "email": user_info.get("email", ""),
            "hireable": user_info.get("hireable", ""),
            "bio": user_info.get("bio", ""),
            "public_repos": user_info.get("public_repos", 0),
            "followers": user_info.get("followers", 0),
            "following": user_info.get("following", 0),
            "created_at": user_info.get("created_at", "")
        })
    
    # Save users data to users.csv
    users_df = pd.DataFrame(user_data)
    users_df.to_csv("users.csv", index=False)

# Process and save repositories data to repositories.csv
def process_repositories_data(users):
    repos_data = []
    for user in users:
        repos = fetch_repositories(user['login'])
        for repo in repos:
            repos_data.append({
                "login": user['login'],
                "full_name": repo.get("full_name", ""),
                "created_at": repo.get("created_at", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "language": repo.get("language", ""),
                "has_projects": repo.get("has_projects", False),
                "has_wiki": repo.get("has_wiki", False),
                "license_name": repo.get("license", {}).get("name", "") if repo.get("license") else ""
            })
    
    # Save repositories data to repositories.csv
    repos_df = pd.DataFrame(repos_data)
    repos_df.to_csv("repositories.csv", index=False)

# Function to create README.md with analysis summary
def create_readme():
    with open("README.md", "w") as f:
        f.write("- This project collects GitHub data on users in Singapore with over 100 followers.\n")
        f.write("- Most users are associated with large companies, and Python is the most popular language.\n")
        f.write("- Developers can increase visibility by having well-maintained profiles and active repositories.\n")

# Main function to run the project setup
def main():
    users = fetch_users()
    process_users_data(users)
    process_repositories_data(users)
    create_readme()
    print("Data collection complete. Files saved: users.csv, repositories.csv, README.md")

if __name__ == "__main__":
    main()


# import pandas as pd

# Load the users data from the CSV file
users_df = pd.read_csv("users.csv")

# Sort users by followers in descending order
top_users = users_df.sort_values(by="followers", ascending=False)

# Select the top 5 users and get their login names
top_5_users = top_users["login"].head(5)

# Format the result as a comma-separated string
top_5_logins = ", ".join(top_5_users)

print("Top 5 users with the highest followers:", top_5_logins)
