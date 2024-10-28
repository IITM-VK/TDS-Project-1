# GitHub User and Repository Data
This repository contains data on GitHub users from Singapore with over 100 followers and their most recent repositories.
Data fetched using the GitHub API.

The users.csv file contains information about users in a specific city with fields like login, name, company, location, email, hireable, bio, public_repos, followers, following, and created_at. The repositories.csv file provides data on these users' repositories, including details like login, full_name, created_at, stargazers_count, watchers_count, language, has_projects, has_wiki, and license_name.

# Key Observations from the Data Analysis
User Dataset:
- There are 694 unique users, primarily located in "Singapore."
- Key fields like company, email, hireable, and bio have significant missing values, with company missing in about 40% of cases.
- The average number of followers per user is 619, with one user having over 101,000 followers, indicating a mix of influential and moderately followed users.

Repositories Dataset:
- There are 39,405 unique repositories from 690 users.
- Programming language information is available for 28,506 repositories, with "JavaScript" being the most common.
- The average star count per repository is 47, though some repositories have over 100,000 stars, showing substantial variance in popularity.
- Licensing information is missing for about 50% of repositories, with "MIT" being the most common license.

# Data Scraping Explanation:
Using GitHub's API, I collected user profiles from a specified city with more than a set number of followers. I then gathered each user's repository data, capturing details like stars and language. This was saved to users.csv and repositories.csv for detailed analysis.

# Interesting Finding: 
The most surprising finding was the high number of users with substantial followings and inactive or poorly starred repositories, highlighting a potential gap between follower count and content engagement.

# Actionable Recommendation: 
Developers can benefit from more active community engagement by regularly updating popular repositories. Focused documentation and feature enhancements in starred repositories can drive user interest and attract new collaborators.
