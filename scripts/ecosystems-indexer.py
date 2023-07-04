from collections import Counter
import json
import os
import pandas as pd
import toml


def process_toml_file(file_path):
    with open(file_path, 'r') as f:
        toml_data = toml.load(f)

        project_title = toml_data.get('title', '')
        sub_ecosystems = toml_data.get('sub_ecosystems', [])
        github_organizations = toml_data.get('github_organizations', [])
        repos = [repo['url'] for repo in toml_data.get('repo', [])]

        json_data = {
            'project_title': project_title,
            'sub_ecosystems': sub_ecosystems,
            'github_organizations': github_organizations,
            'repos': repos
        }

        return json_data

def traverse_directory(directory):
    json_list = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.toml'):
                file_path = os.path.join(root, file)
                json_data = process_toml_file(file_path)
                json_list.append(json_data)

    print(json_data)
    return json_list

from collections import Counter


def extract_github_organizations(result):
    github_organizations = []

    for project in result:
        for organization in project['github_organizations']:
            github_organizations.append(organization)

        for repo_url in project['repos']:
            # extract the organization part from the repo URL
            organization = '/'.join(repo_url.split('/')[:3])  
            github_organizations.append(organization)

    github_organizations_counter = Counter(github_organizations)

    return github_organizations_counter


# create a local copy of https://github.com/electric-capital/crypto-ecosystems/tree/master/data/ecosystems
directory_path = 'ecosystems/'  
result = traverse_directory(directory_path)

# save the result to a JSON file
with open('output.json', 'w') as f:
    json.dump(result, f, indent=4)

print('Conversion completed. JSON file saved as "output.json".')
