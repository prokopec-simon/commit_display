import os
import subprocess
from datetime import datetime
import questionary

# Define the path to search for git repositories
path = r'C:\Users\prokopec.simon\source'

# Define the command to execute
cmd = 'git log --since="1 month 5 days ago" --pretty=format:"%ad: %s" --date=format:"%Y-%m-%d" --all'

# Initialize the dictionary to hold the commit data
commit_data = {}

# Get the list of repositories with commits
repositories_with_commits = []
for root, dirs, files in os.walk(path):
    for dir in dirs:
        # Check if the directory is a git repository
        if dir.endswith('.git'):
            # Get the repository name
            repo_name = os.path.basename(root)
            # Execute the git command and decode the output
            output = subprocess.check_output(
                cmd, cwd=root, shell=True).decode()
            # Check if there are any commits
            if len(output.strip()) > 0:
                repositories_with_commits.append(repo_name)

# Ask user which repositories to ignore
ignore_repositories = questionary.checkbox(
    "Select repositories to ignore",
    choices=repositories_with_commits
).ask()

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

# Print the commit data in order by date
for date in sorted(commit_data.keys()):
    commits = commit_data[date]
    print(f'[{date.strftime("%Y-%m-%d")}]:')
    for commit in commits:
        print(f'    {commit[0]} - {commit[1]}')
