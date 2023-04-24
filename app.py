from flask import Flask, render_template, request
import json
import os
import pandas as pd
import yaml

app = Flask(__name__)

PROJECTS_FILE = 'data/projects.yaml'
GITHUB_DATA_DIR = 'data/github'
LEDGER_DATA_DIR = 'data/ledgers'

def load_projects():
    with open(PROJECTS_FILE, 'r') as f:
        projects_data = yaml.safe_load(f)
    return projects_data['projects']

def get_project_names():
    projects = load_projects()
    return [project['name'] for project in projects]

def get_github_data_path(project_name):
    project = next((project for project in load_projects() if project['name'] == project_name), None)
    if not project:
        return None
    return os.path.join(GITHUB_DATA_DIR, f"{project['repos'][0]['name']}.json")

def get_ledger_data_path(project_name, wallet_address):
    project = next((project for project in load_projects() if project['name'] == project_name), None)
    if not project:
        return None
    ledger = next((ledger for ledger in project['ledgers'] if ledger['address'] == wallet_address), None)
    if not ledger:
        return None
    return os.path.join(LEDGER_DATA_DIR, f"{project_name}-{ledger['name']}.csv")

def load_github_data(project_name):
    path = get_github_data_path(project_name)
    if not path:
        return None
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def load_ledger_data(project_name, wallet_address):
    path = get_ledger_data_path(project_name, wallet_address)
    if not path:
        return None
    try:
        data = pd.read_csv(path)
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.set_index('Date')
        return data
    except:
        return None

def create_commit_graph(project_name):
    data = load_github_data(project_name)
    if not data:
        return None
    df = pd.DataFrame(data['commits'])
    print(df.head())
    df['committed_date'] = pd.to_datetime(df['committed_date'])
    df['committed_date'] = df['committed_date'].dt.date
    df = df.groupby('committed_date').size().reset_index(name='count')

    return df

def create_ledger_graph(project_name, wallet_address):
    data = load_ledger_data(project_name, wallet_address)
    if not data:
        return None
    df = pd.DataFrame(data)
    return df

@app.route("/")
def home():
    project_names = get_project_names()
    selected_project = request.args.get('project', default=None, type=str)
    if not selected_project:
        return render_template('index.html', project_names=project_names)
    commit_data = create_commit_graph(selected_project)
    ledger_data = None
    ledger_address = None
    project = next((project for project in load_projects() if project['name'] == selected_project), None)
    if project and 'ledgers' in project:
        ledger_address = request.args.get('ledger', default=None, type=str)
        if ledger_address:
            ledger_data = create_ledger_graph(selected_project, ledger_address)
    return render_template('index.html', project_names=project_names, 
                           selected_project=selected_project, commit_data=commit_data,
                           ledger_data=ledger_data, ledger_address=ledger_address)

if __name__ == "__main__":
    app.run(debug=True)
