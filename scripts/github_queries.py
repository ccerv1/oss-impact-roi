import json
import os
import requests
from scripts.querystrings import query_commits, query_pull_requests

DATA_PATH = "data/github"


QUERIES = [
    {
        "name": "commits",
        "func": query_commits,
        "directory": "commits",
        "date_key": "committed_date"
    }, 
    {
        "name": "pull requests",
        "func": query_pull_requests,
        "directory": "PRs",
        "date_key": "mergedAt"
    }
]


def data_already_exists(data_file, start_date, end_date):
    if not os.path.isfile(data_file):
        return False
    with open(data_file, 'r') as f:
        data = json.load(f)
    return data['date_range'] == [start_date, end_date]


def get_data_for_repos(token, owner, repos, start_date, end_date):
    
    for query in QUERIES:

        data_file = "/".join([DATA_PATH, query["directory"], f"{owner}.json"])
        if data_already_exists(data_file, start_date, end_date):
            continue

        data = []
        for repo_name in repos:
            results, status = query_repo(query, token, owner, repo_name, start_date, end_date)
            if status != "OK":
                return
            
            print(f"Fetched {len(results)} {query['name']} for repo {repo_name}.")
            if len(results):
                data.extend(results)
        
        json_data = {
            "owner": owner,
            "date_range": [start_date, end_date],
            "repos": repos,
            "data": data            
        }       
        with open(data_file, 'w') as f:
            json.dump(json_data, f, indent=4)


def query_repo(query, token, owner, repo_name, start_date, end_date):
    items = []
    end_cursor = "null"
    has_next_page = True
    while has_next_page:
        func = query["func"]
        query_string = func(
            owner=owner, 
            name=repo_name, 
            first=100, 
            after=end_cursor, 
            since=start_date, 
            until=end_date
        )
        response = requests.post(
            'https://api.github.com/graphql', 
            json={'query': query_string}, 
            headers={'Authorization': f'token {token}'}
        )
        response_json = response.json()
        if not response_json.get('data'):
            print(f"Failed to retrieve items for {repo_name}. {response_json.get('message')}")
            print(query_string)
            print(response_json)
            if "rate limit" in response_json.get('message', ''):
                return items, "rate limit"
            break

        data = find_dict_with_pageinfo(response_json['data'])

        if not data:
            print(f"No items found for {repo_name}.")
            break
        key = "edges" if "edges" in data.keys() else "nodes"
        for item in data[key]:
            item['repo'] = repo_name
            flattened_item = flatten_dict(item)
            items.append(flattened_item)

        has_next_page = data['pageInfo']['hasNextPage']
        if has_next_page:
            end_cursor = data['pageInfo']['endCursor']
            end_cursor = f'"{end_cursor}"'

    status = "OK"
    return items, status  


def find_dict_with_pageinfo(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if v and 'pageInfo' in v:
                return data[k]
            else:
                result = find_dict_with_pageinfo(v)
                if result is not None:
                    return result
    return None


def flatten_dict(d):
    flattened_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            inner_dict = flatten_dict(value)
            flattened_dict.update({f"{key}_{inner_key}": inner_value for inner_key, inner_value in inner_dict.items()})
        elif isinstance(value, list):
            flattened_dict.update({f"{key}_{i}": item for i, item in enumerate(value)})
        else:
            flattened_dict[key] = value
    return flattened_dict      