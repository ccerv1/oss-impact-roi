from datetime import datetime
from dotenv import load_dotenv
import json
import os
import re
import yaml

from scripts.retrieve_repos import retrieve_repos
from scripts.github_queries import get_data_for_repos
from scripts.retrieve_wallet_history import retrieve_wallet_history


START, END = '2022-01-01T00:00:00Z', '2023-04-22T00:00:00Z'


def populate_data(token):
    yaml_data = load_projects_data()
    all_projects = yaml_data['projects']
    for (i, project) in enumerate(all_projects):     
        print(f"\n\n{i+1}/{len(all_projects)} Analyzing project {project['name']}:")
        for repo_data in project['repos']:
            repo_owner = repo_data['name']
            repo_path = repo_data['url'].replace("https://github.com/","")
            if "/" in repo_path:
                repos = [repo_path.split("/")[1]]
            else:
                repos = retrieve_repos(repo_owner, token)
            get_data_for_repos(token, repo_owner, repos, START, END)


def load_projects_data():
    with open('data/projects.yaml', 'r') as f:
        projects_data = yaml.safe_load(f)
    return projects_data


def download_wallet_history():
    projects_data = load_projects_data()
    for project_data in projects_data['projects']:
        project_name = project_data['name']
        for wallet in project_data['ledgers']:
            address = wallet['address']
            if len(address) != 42:
                print(f"{project_name} - {address} is not a valid Ethereum address")
                continue
            retrieve_wallet_history(project_name, address)
        

if __name__ == '__main__':
    load_dotenv()
    download_wallet_history()
    token = os.getenv('GITHUB_TOKEN')
    populate_data(token)
    

