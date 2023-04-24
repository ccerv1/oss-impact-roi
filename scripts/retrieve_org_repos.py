import requests

def retrieve_org_repos(owner, token):
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
        }
    """

    repos = []
    end_cursor = None
    has_next_page = True
    while has_next_page:
        variables = {'owner': owner}
        if end_cursor:
            variables['after'] = end_cursor

        headers = {'Authorization': f'token {token}'}
        response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
        response_json = response.json()

        if 'data' not in response_json or not response_json['data'].get('organization'):
            print(f"Failed to retrieve repos for: `{owner}`. Message: {response_json.get('message')}")
            break

        data = response_json['data']['organization']['repositories']

        if not data:
            print(f"No repositories found for {owner}.")
            break

        if not data.get('pageInfo'):
            print(f"Invalid response format: missing pageInfo object in response from {owner}.")
            break

        has_next_page = data['pageInfo']['hasNextPage']
        if has_next_page:
            end_cursor = data['pageInfo']['endCursor']

        for repo in data.get('nodes', []):
            repo_data = {'name': repo['name'], 'url': repo['url']}
            repos.append(repo_data)

    return repos