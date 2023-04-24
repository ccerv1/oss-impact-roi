import requests

def retrieve_commits_for_repo(owner, repo, start_date, end_date, token):
    query = """
        query ($owner: String!, $name: String!, $first: Int!, $after: String, $since: GitTimestamp!, $until: GitTimestamp!) {
          repository(owner: $owner, name: $name) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: $first, after: $after, since: $since, until: $until) {
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    edges {
                      node {
                        committedDate
                        author {
                          user {
                              name
                              login
                            }
                        }
                        additions
                        deletions
                        message
                        oid
                        url
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    commits = []
    end_cursor = None
    has_next_page = True
    while has_next_page:
        variables = {'owner': owner, 'name': repo, 'first': 100, 'since': start_date, 'until': end_date}
        if end_cursor:
            variables['after'] = end_cursor

        headers = {'Authorization': f'token {token}'}
        response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
        response_json = response.json()

        if 'data' not in response_json:
            print(f"Failed to retrieve commits for {repo}. {response_json.get('message')}")
            break

        data = response_json['data']['repository']['defaultBranchRef']['target']['history']

        if not data:
            print(f"No commits found for {repo}.")
            break

        if not data.get('pageInfo'):
            print(f"Invalid response format: missing pageInfo object in response from {repo}.")
            break

        has_next_page = data['pageInfo']['hasNextPage']
        if has_next_page:
            end_cursor = data['pageInfo']['endCursor']

        for commit in data.get('edges', []):
            commit_data = commit['node']
            commit_data['repo'] = repo
            commits.append(commit_data)

    return commits