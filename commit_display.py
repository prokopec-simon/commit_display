import os
from datetime import datetime, timedelta

# Set the base directory to search for Git repositories
base_dir = r"C:\Users\prokopec.simon\source"

# Get a list of all Git repositories under the base directory
git_repos = [os.path.join(dp, d) for dp, dn, filenames in os.walk(
    base_dir) for d in dn if '.git' in os.listdir(os.path.join(dp, d))]

# Group the commits by date and repository name
commit_groups = {}
for repo in git_repos:
    os.chdir(repo)
    output = os.popen(
        'git log --since="1 month ago" --pretty=format:"%ad: %s" --date=format:"%Y-%m-%d" --all').read().strip()
    if output:
        for commit in output.split('\n'):
            commit_date, commit_msg = commit.split(': ', maxsplit=1)
            commit_groups.setdefault(commit_date, {}).setdefault(
                repo, []).append(commit_msg)

# Print the grouped commits
for commit_date, repos in commit_groups.items():
    print(f"[{commit_date}]:")
    for repo, commit_msgs in repos.items():
        for commit_msg in commit_msgs:
            print(f"    {os.path.basename(repo)} - {commit_msg}")
