import os
import subprocess
from datetime import datetime
import questionary

os.system('cls')

# Set the default path to the current working directory
default_path = os.getcwd()
path_components = default_path.split("\\")

# For some reason the joined path was missing \ after C:
if not path_components[0].endswith("\\"):
    path_components[0] += "\\"

# Remove the last element (file name) and rejoin the path components
default_path = os.path.join(*path_components[:-1]) + "\\"
# Ask user for the path to search for git repositories with the default value
path = questionary.text("Enter the path to search for git repositories:", default=default_path).ask()

# Validate if the path exists
while not os.path.exists(path):
    print("Invalid path. Please enter a valid path.")
    path = questionary.text("Enter the path to search for git repositories:", default=default_path).ask()

# Define the git command to browse for data in the last month and five days
cmd = 'git log --since="1 month 5 days ago" --pretty=format:"%ad: %an - %s" --date=format:"%Y-%m-%d" --all'

# Initialize the dictionaries to hold the commit data and user data
commit_data = {}
repositories_with_commits = []
distinct_commit_authors = []

os.system('cls')
print('Loading repositories...')

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
                            if name not in distinct_commit_authors:
                                distinct_commit_authors.append(name)
                    repositories_with_commits.append({'name': repo_name, 'commits_from': authors})
            except subprocess.CalledProcessError as e:
                print(f"Error executing git command in {repo_name}: {e}")
                continue

os.system('cls')
# Ask user which users to show components for
users_to_show = questionary.checkbox(
    "Select users to show commits for",
    choices=distinct_commit_authors
).ask()

# Ask user which repositories to ignore
ignore_repositories = questionary.checkbox(
    "Select repositories to ignore",
    choices=[repo['name'] for repo in repositories_with_commits if any(user in users_to_show for user in repo['commits_from'])]
).ask()

#ignoring repositories that have no commits from selected users
repositories_without_any_commits_from_selected_users = [repo['name'] for repo in repositories_with_commits if not any(user in users_to_show for user in repo['commits_from'])]
ignore_repositories.extend(repositories_without_any_commits_from_selected_users)

os.system('cls')
print('Loading individual commits...')
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
            # If there is only one author do not print the name in the output
            print(f'    {commit[0]} - {commit[1].split(" - ")[1]}')
        else:
            # Include author if more than one author is selected
            print(f'    {commit[0]} - {commit[1]}')
