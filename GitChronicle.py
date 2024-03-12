import os
import subprocess
from datetime import datetime
import questionary

os.system('cls')
print('Loading repositories...')

# Define the path to search for git repositories
path = r'C:\Users\prokopec.simon\source'

# Define the command to execute
cmd = 'git log --since="1 month 5 days ago" --pretty=format:"%ad: %an - %s" --date=format:"%Y-%m-%d" --all'

# Initialize the dictionaries to hold the commit data and user data
commit_data = {}
repositories_with_commits = []
user_data = []

# Get the list of repositories with commits
for root, dirs, files in os.walk(path):
    for dir in dirs:
        # Check if the directory is a git repository
        if dir.endswith('.git'):
            # Get the repository name
            repo_name = os.path.basename(root)
            # Execute the git command and decode the output
            try:
                output = subprocess.check_output(
                    cmd, cwd=root, shell=True).decode()
                if len(output.strip()) > 0:
                    # Extract and add authors (users) to the set
                    authors = set()
                    for line in output.splitlines():
                        line = line.strip()
                        if line:
                            parts = line.split(':')
                            name = parts[1].split(' - ')[0].strip()
                            authors.add(name)
                            if name not in user_data:
                                user_data.append(name)
                    repositories_with_commits.append({'name': repo_name, 'commits_from': authors})
            except subprocess.CalledProcessError as e:
                print(f"Error executing git command in {repo_name}: {e}")
                continue

os.system('cls')
# Ask user which users to show components for
users_to_show = questionary.checkbox(
    "Select users to show commits for",
    choices=user_data
).ask()

# Ask user which repositories to ignore
ignore_repositories = questionary.checkbox(
    "Select repositories to ignore",
    choices=[repo['name'] for repo in repositories_with_commits if any(user in users_to_show for user in repo['commits_from'])]
).ask()

repositories_without_any_commits_from_selected_users = [repo['name'] for repo in repositories_with_commits if not any(user in users_to_show for user in repo['commits_from'])]
ignore_repositories.extend(repositories_without_any_commits_from_selected_users)

os.system('cls')
print('Loading individual commits...')

# Loop through each repository

# Loop through each repository
for root, dirs, files in os.walk(path):
    for dir in dirs:
        # Check if the directory is a git repository
        if dir.endswith('.git'):
            # Get the repository name
            repo_name = os.path.basename(root)
            if repo_name in ignore_repositories:
                continue
            # Execute the git command and decode the output
            output = subprocess.check_output(
                cmd, cwd=root, shell=True).decode()
            # Split the output by newline characters
            output_lines = output.split('\n')
            # Loop through each line of output and extract the commit data
            for line in output_lines:
                line = line.strip()
                if line != '':
                    # Extract the date and commit message
                    date_str, message = line.split(': ', 1)
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Add the commit data to the dictionary
                    if date not in commit_data:
                        commit_data[date] = []
                    commit_data[date].append((repo_name, message))

os.system('cls')

# Print the commit data in order by date
for date in sorted(commit_data.keys()):
    commits = commit_data[date]
    print(f'[{date.strftime("%Y-%m-%d")}]:')
    for commit in commits:
        if(len(users_to_show)==1):
            print(f'    {commit[0]} - {commit[1].split(" - ")[1]}')
        else:
            print(f'    {commit[0]} - {commit[1]}')
