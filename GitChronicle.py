import os
import subprocess
from datetime import datetime
import questionary

def get_default_path():
    default_path = os.getcwd()
    path_components = default_path.split("\\")
    if not path_components[0].endswith("\\"):
        path_components[0] += "\\"
    return os.path.join(*path_components[:-1]) + "\\"

def get_valid_path():
    path = questionary.text("Enter the path to search for git repositories:", default=get_default_path()).ask()
    while not os.path.exists(path):
        print("Invalid path. Please enter a valid path.")
        path = questionary.text("Enter the path to search for git repositories:", default=get_default_path()).ask()
    return path

def get_repositories_with_commits(path, cmd):
    repositories_with_commits = []
    distinct_commit_authors = []

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith('.git'):
                repo_name = os.path.basename(root)
                try:
                    output = subprocess.check_output(cmd, cwd=root, shell=True).decode()
                    if len(output.strip()) > 0:
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

    return repositories_with_commits, distinct_commit_authors

def get_users_to_show(distinct_commit_authors):
    return questionary.checkbox("Select users to show commits for", choices=distinct_commit_authors).ask()

def get_ignore_repositories(repositories_with_commits, users_to_show):
    return questionary.checkbox(
        "Select repositories to ignore",
        choices=[repo['name'] for repo in repositories_with_commits if any(user in users_to_show for user in repo['commits_from'])]
    ).ask()

def get_repositories_without_commits(repositories_with_commits, users_to_show):
    return [repo['name'] for repo in repositories_with_commits if not any(user in users_to_show for user in repo['commits_from'])]

def load_commits(path, ignore_repositories, cmd):
    commit_data = {}

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith('.git'):
                repo_name = os.path.basename(root)
                if repo_name in ignore_repositories:
                    continue
                output = subprocess.check_output(cmd, cwd=root, shell=True).decode()
                output_lines = output.split('\n')
                for line in output_lines:
                    line = line.strip()
                    if line != '':
                        date_str, message = line.split(': ', 1)
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        if date not in commit_data:
                            commit_data[date] = []
                        commit_data[date].append((repo_name, message))

    return commit_data

def print_commit_data(commit_data, users_to_show):
    os.system('cls')
    for date in sorted(commit_data.keys()):
        commits = commit_data[date]
        print(f'[{date.strftime("%Y-%m-%d")}]:')
        for commit in commits:
            if(len(users_to_show)==1):
                print(f'    {commit[0]} - {commit[1].split(" - ")[1]}')
            else:
                print(f'    {commit[0]} - {commit[1]}')

def main():
    os.system('cls')
    path = get_valid_path()

    cmd = 'git log --since="1 month 5 days ago" --pretty=format:"%ad: %an - %s" --date=format:"%Y-%m-%d" --all'


    os.system('cls')
    print('Loading repositories...')
    repositories_with_commits, distinct_commit_authors = get_repositories_with_commits(path, cmd)

    users_to_show = get_users_to_show(distinct_commit_authors)
    ignore_repositories = get_ignore_repositories(repositories_with_commits, users_to_show)

    repositories_without_commits = get_repositories_without_commits(repositories_with_commits, users_to_show)
    ignore_repositories.extend(repositories_without_commits)

    os.system('cls')
    print('Loading individual commits...')

    commit_data = load_commits(path, ignore_repositories, cmd)

    print_commit_data(commit_data, users_to_show)

if __name__ == "__main__":
    main()
