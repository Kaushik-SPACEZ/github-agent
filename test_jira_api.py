"""
Test script for Jira API integration
Tests connection and ticket creation
"""

import os
from dotenv import load_dotenv
from agent.tools import jira_integration

# Load environment variables
load_dotenv()

def test_jira_connection():
    """Test Jira connection"""
    print("=" * 60)
    print("Testing Jira Connection")
    print("=" * 60)
    
    jira_config = {
        'JIRA_BASE_URL': os.getenv('JIRA_BASE_URL', ''),
        'JIRA_EMAIL': os.getenv('JIRA_EMAIL', ''),
        'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN', ''),
        'JIRA_PROJECT_KEY': os.getenv('JIRA_PROJECT_KEY', '')
    }
    
    # Check if all config is present
    if not all(jira_config.values()):
        print("❌ Missing Jira configuration in .env file")
        print("\nRequired variables:")
        for key, value in jira_config.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {'Set' if value else 'Missing'}")
        return False
    
    print("\n✅ All Jira config variables found")
    print(f"\nJira URL: {jira_config['JIRA_BASE_URL']}")
    print(f"Email: {jira_config['JIRA_EMAIL']}")
    print(f"Project: {jira_config['JIRA_PROJECT_KEY']}")
    
    # Test connection
    print("\n🔗 Testing connection...")
    result = jira_integration.test_jira_connection(jira_config)
    
    if result['success']:
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ {result['message']}")
        return False


def test_create_ticket():
    """Test creating a Jira ticket"""
    print("\n" + "=" * 60)
    print("Testing Ticket Creation")
    print("=" * 60)
    
    jira_config = {
        'JIRA_BASE_URL': os.getenv('JIRA_BASE_URL', ''),
        'JIRA_EMAIL': os.getenv('JIRA_EMAIL', ''),
        'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN', ''),
        'JIRA_PROJECT_KEY': os.getenv('JIRA_PROJECT_KEY', '')
    }
    
    # Sample issue from code scanner
    test_issue = {
        'type': 'security',
        'severity': 'critical',
        'file': 'test_groq_api.py',
        'location': 'line 15',
        'description': 'API key is printed to the console which exposes sensitive credentials',
        'suggestion': 'Remove all print statements that output API keys or other sensitive data. Use environment variables and never log credentials.'
    }
    
    print("\n📝 Creating test ticket...")
    print(f"   File: {test_issue['file']}")
    print(f"   Severity: {test_issue['severity']}")
    print(f"   Type: {test_issue['type']}")
    
    result = jira_integration.create_jira_ticket(test_issue, jira_config)
    
    if result['success']:
        print(f"\n✅ Ticket created successfully!")
        print(f"   Ticket Key: {result['ticket_key']}")
        print(f"   Ticket URL: {result['ticket_url']}")
        print(f"\n🔗 View ticket: {result['ticket_url']}")
        return True
    else:
        print(f"\n❌ Failed to create ticket")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False


def main():
    """Run all tests"""
    print("\n🧪 Jira API Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Connection
    connection_ok = test_jira_connection()
    
    if not connection_ok:
        print("\n⚠️  Connection test failed. Skipping ticket creation test.")
        return
    
    # Test 2: Create ticket
    input("\n⏸️  Press Enter to create a test ticket in Jira...")
    ticket_ok = test_create_ticket()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Connection Test: {'✅ PASSED' if connection_ok else '❌ FAILED'}")
    print(f"Ticket Creation: {'✅ PASSED' if ticket_ok else '❌ FAILED'}")
    print("=" * 60)
    
    if connection_ok and ticket_ok:
        print("\n🎉 All tests passed! Jira integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()