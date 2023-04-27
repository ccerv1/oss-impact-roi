import json
import requests


def retrieve_repos(owner, token):
    query = """
        query ($owner: String!, $after: String) {
          organization(login: $owner) {
            repositories(first: 100, after: $after) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                name
                url
              }
            }
          }
          user(login: $owner) {
            repositories(first: 100, after: $after) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                name
                url
              }
            }
          }
        }
    """

    repos = []
    end_cursor = None
    has_next_page = True
    count = 0
    while has_next_page:
        count += 1
        variables = {'owner': owner}
        if end_cursor:
            variables['after'] = end_cursor

        headers = {'Authorization': f'token {token}'}
        response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)

        try:
            response_json = response.json()
            response.raise_for_status()
        except:
            print(f"Failed to retrieve repos for: `{owner}`. Response JSON: {json.dumps(response.json(), indent=2)}")
            break

        owner_data = response_json['data']
        if owner_data['organization']:
            data = owner_data['organization']['repositories']
            print(f"Gathering repos (page {count}) for organization: {owner}")
        elif owner_data['user']:
            data = owner_data['user']['repositories']    
            print(f"Gathering repos (page {count}) for user: {owner}")
        else:
            print(f"No repositories found for {owner}.")
            break

        if not data.get('pageInfo'):
            print(f"Invalid response format: missing pageInfo object in response from {owner}.")
            break

        has_next_page = data['pageInfo']['hasNextPage']
        if has_next_page:
            end_cursor = data['pageInfo']['endCursor']

        for repo in data.get('nodes', []):
            #repo_data = {'name': repo['name'], 'url': repo['url']}
            repos.append(repo['name'])

    return repos
