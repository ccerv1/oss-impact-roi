from datetime import datetime
from dotenv import load_dotenv
import json
import pandas as pd
import os
import re
import yaml

from scripts.retrieve_repos import retrieve_repos
from scripts.github_queries import get_data_for_repos
from scripts.retrieve_wallet_history import retrieve_wallet_history
from scripts.retrieve_address_data import retrieve_address_data


START, END = '2022-01-01T00:00:00Z', '2023-04-22T00:00:00Z'

OVERRIDES = {
    "0xC988107688b750dee6237B85A3ca49ba0a6": "0xC988107688b750dee6237B85A3ca49ba0a65DaB0",
    "0xf508311867EFdC50cf36B06EC95E0EEdb22": "0xf508311867EFdC50cf36B06EC95E0EEdb2212599",
    "0xfB0dADb835fAdE151aBf6780BeAfB12FC5B": "0xfB0dADb835fAdE151aBf6780BeAfB12FC5BA0e1F",
    "0x3a153B0608a87a4BdD4F7Afa90670110d4C": "0x3a153B0608a87a4BdD4F7Afa90670110d4CBEa62",
    "0x3EDf6868d7c42863E44072DaEcC16eCA280": "0x3EDf6868d7c42863E44072DaEcC16eCA2804Dea1",
    "0xfd0CF79C568c08b78484F2D165eB8c7f569": "UNKNOWN"
}


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
    for project_data in reversed(projects_data['projects']):
        project_name = project_data['name']
        for wallet in project_data['ledgers']:
            address = wallet['address']
            if len(address) != 42:
                address = OVERRIDES.get(address)
                if not address:
                    print(f"{project_name} - {address} is not a valid Ethereum address")
                    continue
            retrieve_wallet_history(project_name, address)


def store_wallet_stats():
    datestamp = datetime.strftime(datetime.now(),"%Y-%m-%d")
    projects_data = load_projects_data()
    wallet_data = []    
    for project_data in projects_data['projects']:
        project_name = project_data['name']
        for wallet in project_data['ledgers']:
            override = False
            address = wallet['address']
            if len(address) != 42:
                address = OVERRIDES.get(address)
                if address:
                    override = True
                else:
                    print(f"{project_name} - {address} is not a valid Ethereum address")
            data = retrieve_address_data(address)
            data.update({"name": project_name, "date": datestamp})
            if override:
                data.update({"type": "opSafe"})
            wallet_data.append(data)
    df = pd.DataFrame(wallet_data)
    outpath = f"data/ledgers/web3/{datestamp}_wallet_stats.csv"
    df.to_csv(outpath)
    print("Successfully saved", len(df), "records to:", outpath)


if __name__ == '__main__':
    load_dotenv()    
    # token = os.getenv('GITHUB_TOKEN')
    # populate_data(token)
    download_wallet_history()
    store_wallet_stats()
    

