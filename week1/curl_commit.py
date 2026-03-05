import requests
import re
from datetime import datetime, timedelta

def fetch_repo_data(repo_url):
    """
    Simple script to fetch branches and commits from a public GitHub repository.
    Uses GitHub REST API.
    """
    # Extract owner and repo from URL (e.g., https://github.com/owner/repo)
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        print("Invalid GitHub repository URL.")
        return

    owner = match.group(1)
    repo = match.group(2).replace('.git', '')
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        print(f"\n--- Fetching branches for {owner}/{repo} ---")
        
        # 1. Get all branches
        branches_response = requests.get(f"{base_url}/branches")
        if branches_response.status_code != 200:
            print(f"Failed to fetch branches: {branches_response.reason}")
            return
        
        branches = branches_response.json()
        branch_names = [b['name'] for b in branches]

        print(f"Branches found: {', '.join(branch_names)}")

        # 2. Get commits for each branch
        for branch in branch_names:
            print(f"\n\n>>> Commits on branch: {branch} <<<")
            
            commits_response = requests.get(f"{base_url}/commits", params={'sha': branch})
            if commits_response.status_code != 200:
                print(f"Failed to fetch commits for branch {branch}")
                continue

            commits = commits_response.json()

            for item in commits:
                commit = item['commit']
                author = commit['author']
                
                # Format date to UTC+7 for better readability
                raw_date = author['date']
                dt_utc = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
                dt_gmt7 = dt_utc + timedelta(hours=7)
                formatted_date = dt_gmt7.strftime("%d/%m/%Y %H:%M:%S")

                print("-----------------------------------------")
                print(f"Author: {author['name']} <{author['email']}>")
                print(f"Date:   {formatted_date} (GMT+7)")
                print(f"Message: {commit['message']}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    repo_link = "https://github.com/Anhnguyen0812/2526II_INT3505_1"
    fetch_repo_data(repo_link)

