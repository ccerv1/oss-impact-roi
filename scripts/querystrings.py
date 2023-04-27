# GraphQL Query Strings


def query_commits(owner, name, first, after, since, until):
    return f'''
        {{
            repository(
                owner: "{owner}"
                name: "{name}"
            ) {{
            defaultBranchRef {{
              target {{
                ... on Commit {{
                    history(
                        first: {first}
                        after: {after}
                        since: "{since}"
                        until: "{until}"
                    ) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    edges {{
                      node {{
                        committedDate
                        author {{
                          user {{
                              name
                              login
                            }}
                        }}
                        additions
                        deletions
                        message
                        oid
                        url
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
    '''


def query_pull_requests(owner, name, first, after, since, until):
    return f'''
        {{
          search(
            query: "repo:{owner}/{name} is:pr is:merged merged:{since}..{until}" 
            first: {first}
            after: {after}
            type: ISSUE
          ) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            nodes {{
              ... on PullRequest {{
                title
                url
                createdAt
                mergedAt
                mergedBy {{
                  login
                }}
                author {{
                  login
                }}
              }}
            }}
          }}
        }}
    '''