# ============================================================
# jira_integration.py — Jira Integration for Issue Creation
# ============================================================
# PURPOSE:
#   Creates Jira tickets from code quality issues detected by the scanner.
#
# INPUT:  Issues list, Jira credentials, assignee (optional)
# OUTPUT: Created ticket IDs and URLs
# ============================================================

import os
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json


def get_user_account_id(email_or_name, jira_config):
    """
    Get Jira user account ID from email or display name.
    
    Args:
        email_or_name: User email or display name
        jira_config: Jira configuration dict
    
    Returns:
        Account ID string or None if not found
    """
    base_url = jira_config['JIRA_BASE_URL']
    auth = HTTPBasicAuth(jira_config['JIRA_EMAIL'], jira_config['JIRA_API_TOKEN'])
    
    # Try to search for user
    url = f"{base_url}/rest/api/3/user/search"
    params = {"query": email_or_name}
    
    try:
        response = requests.get(url, auth=auth, params=params, timeout=5)
        if response.status_code == 200:
            users = response.json()
            if users and len(users) > 0:
                # Return the first match's account ID
                return users[0].get('accountId')
    except:
        pass
    
    return None


def create_jira_ticket(issue, jira_config, assignee=None):
    """
    Create a single Jira ticket for a code quality issue.
    
    Args:
        issue: Dict with keys: type, severity, file, location, description, suggestion
        jira_config: Dict with JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY
        assignee: Optional Jira username/email to assign the ticket to
    
    Returns:
        Dict with success status, ticket_key, and ticket_url
    """
    
    base_url = jira_config['JIRA_BASE_URL']
    email = jira_config['JIRA_EMAIL']
    api_token = jira_config['JIRA_API_TOKEN']
    project_key = jira_config['JIRA_PROJECT_KEY']
    
    # Map severity to Jira priority
    priority_map = {
        'critical': 'Highest',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    }
    
    severity = issue.get('severity', 'medium')
    issue_type = issue.get('type', 'complexity')
    
    # Use "Task" - confirmed available in CICD project
    jira_issue_type = "Task"
    
    # Build ticket summary (concise, actionable)
    file_name = issue.get('file', 'Unknown file')
    issue_desc = issue.get('description', 'No description')
    summary = f"[{severity.upper()}] {file_name}: {issue_desc[:80]}"
    
    # Build structured ticket description with proper sections
    description = f"""h2. 🔍 Issue Overview

*Severity:* {severity.upper()}
*Type:* {issue_type}
*File:* {{code}}{file_name}{{code}}
*Location:* {issue.get('location', 'Not specified')}

----

h2. 📋 Problem Description

{issue.get('description', 'No description provided')}

----

h2. 🎯 Impact

This {severity}-severity {issue_type} issue can lead to:
• Code maintainability problems
• Potential runtime errors
• Security vulnerabilities (if applicable)
• Technical debt accumulation

----

h2. ✅ Recommended Solution

{issue.get('suggestion', 'No specific suggestion provided. Please review the code and apply best practices.')}

----

h2. 📝 Steps to Reproduce/Verify

1. Open the file: {{code}}{file_name}{{code}}
2. Navigate to: {issue.get('location', 'the specified location')}
3. Review the code section mentioned above
4. Apply the recommended fix
5. Run tests to verify the fix

----

h2. 🔗 Additional Context

*Detection Method:* Automated code quality analysis
*Analysis Date:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Tool:* Code Quality Monitor AI Agent

----

_This ticket was automatically created by the autonomous AI agent. Please review and update as needed._
"""
    
    # Prepare Jira API request
    url = f"{base_url}/rest/api/3/issue"
    
    auth = HTTPBasicAuth(email, api_token)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": jira_issue_type
            },
            "priority": {
                "name": priority_map.get(severity, 'Medium')
            }
        }
    }
    
    # Add assignee if provided - lookup account ID from email/name
    if assignee:
        account_id = get_user_account_id(assignee, jira_config)
        if account_id:
            payload["fields"]["assignee"] = {
                "id": account_id
            }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            data=json.dumps(payload),
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            ticket_key = result.get('key')
            ticket_url = f"{base_url}/browse/{ticket_key}"
            
            return {
                'success': True,
                'ticket_key': ticket_key,
                'ticket_url': ticket_url,
                'message': f"Created ticket {ticket_key}"
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}",
                'message': f"Failed to create ticket"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Exception: {str(e)}"
        }


def create_bulk_tickets(issues, jira_config, assignees=None):
    """
    Create multiple Jira tickets from a list of issues.
    
    Args:
        issues: List of issue dicts
        jira_config: Jira configuration dict
        assignees: Optional dict mapping issue index to assignee
    
    Returns:
        List of results for each ticket creation
    """
    results = []
    
    for i, issue in enumerate(issues):
        assignee = assignees.get(i) if assignees else None
        result = create_jira_ticket(issue, jira_config, assignee)
        results.append({
            'issue': issue,
            'result': result
        })
    
    return results


def test_jira_connection(jira_config):
    """
    Test Jira connection and credentials.
    
    Returns:
        Dict with success status and message
    """
    base_url = jira_config['JIRA_BASE_URL']
    email = jira_config['JIRA_EMAIL']
    api_token = jira_config['JIRA_API_TOKEN']
    
    url = f"{base_url}/rest/api/3/myself"
    auth = HTTPBasicAuth(email, api_token)
    
    try:
        response = requests.get(url, auth=auth, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                'success': True,
                'message': f"Connected as {user_data.get('displayName', 'Unknown')}",
                'user': user_data
            }
        else:
            return {
                'success': False,
                'message': f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Connection failed: {str(e)}"
        }