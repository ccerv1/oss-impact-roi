from datetime import datetime
from dotenv import load_dotenv
import json
import os
import re
import yaml

from scripts.retrieve_org_repos import retrieve_org_repos
from scripts.retrieve_commits_for_repo import retrieve_commits_for_repo
from scripts.retrieve_wallet_history import retrieve_wallet_history

START, END = '2022-01-01T00:00:00Z', '2023-04-22T00:00:00Z'


def populate_data(token):    
    projects_data = load_projects_data()
    for project_data in projects_data['projects']:
        repo_owner, repos = get_repos_for_project(project_data, token)
        if not should_update_data(repo_owner):
            continue
        flattened_commits = get_commits_for_repos(repos, repo_owner, token)
        results = {
            "commits": flattened_commits,
            "date_range": [START, END],
            "repos": repos
        }
        save_data(results, repo_owner)


def should_update_data(repo_owner):
    data_file = f'data/github/{repo_owner}.json'
    if not os.path.isfile(data_file):
        return True
    with open(data_file, 'r') as f:
        data = json.load(f)
    return data['date_range'] != [START, END]


def load_projects_data():
    with open('data/projects.yaml', 'r') as f:
        projects_data = yaml.safe_load(f)
    return projects_data


def get_repos_for_project(project_data, token):
    repo_owner = project_data['repos'][0]['name']
    repos = retrieve_org_repos(repo_owner, token)
    return repo_owner, repos


def get_commits_for_repos(repos, repo_owner, token):
    flattened_commits = []
    for repo in repos:
        repo_name = repo['name']
        try:
            commits = retrieve_commits_for_repo(repo_owner, repo_name, START, END, token)
            print(f"Fetched {len(commits)} commits from repo {repo_name}.")
        except:
            print(f"Encountered an error fetching commits from repo {repo_name}")
            continue
        for commit in commits:
            try:
                author = commit['author']['user']['login']
            except:
                author = "na"
            flattened_commit = {
                'owner': repo_owner,
                'repo': repo_name,
                'url': repo['url'],
                'committed_date': commit['committedDate'],
                'author': author,
                'additions': commit['additions'],
                'deletions': commit['deletions'],
                'message': commit['message'],
                'oid': commit['oid'],
                'url': commit['url']
            }
            flattened_commits.append(flattened_commit)
    return flattened_commits


def save_data(results, repo_owner):
    with open(f'data/github/{repo_owner}.json', 'w') as f:
        json.dump(results, f, indent=4)


def download_wallet_history():
    projects_data = load_projects_data()
    for project_data in projects_data['projects']:
        project_name = project_data['name']
        for wallet in project_data['ledgers']:
            address = wallet['address']
            if len(address) != 42:
                print(f"{project_name} - {address} is not a valid Ethereum address")
                continue
            try:
                retrieve_wallet_history(project_name, address)
            except:
                print(f"Encountered an error with: {project_name} - {address}.")
        

if __name__ == '__main__':    
    # load_dotenv()
    # token = os.getenv('GITHUB_TOKEN')
    # populate_data(token)
    download_wallet_history()
