import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
api_token = os.getenv('JIRA_API_TOKEN')
project_key = os.getenv('JIRA_PROJECT_KEY')

url = f'{base_url}/rest/api/3/project/{project_key}'
auth = HTTPBasicAuth(email, api_token)
response = requests.get(url, auth=auth)

if response.status_code == 200:
    project = response.json()
    issue_types = project.get('issueTypes', [])
    print('\nAvailable Issue Types:')
    for it in issue_types:
        print(f'  - {it["name"]}')
else:
    print(f'Error: {response.status_code}')