"""
API endpoints with security and validation issues.
Issues: No input validation, security vulnerabilities, missing error handling
"""

import json

class UserAPI:
    """
    ISSUE: No docstring for class
    ISSUE: Methods lack proper error handling
    """
    
    def __init__(self):
        self.users = {}
    
    def create_user(self, user_data):
        """
        ISSUE: No input validation
        ISSUE: No error handling
        ISSUE: No authentication check
        """
        user_id = user_data["id"]  # ISSUE: KeyError if 'id' missing
        self.users[user_id] = user_data
        return {"status": "success", "user_id": user_id}
    
    def get_user(self, user_id):
        """
        ISSUE: No error handling for missing user
        """
        return self.users[user_id]  # ISSUE: KeyError if user doesn't exist
    
    def update_user(self, user_id, updates):
        """
        ISSUE: No validation of updates
        ISSUE: No check if user exists
        """
        self.users[user_id].update(updates)
        return {"status": "updated"}
    
    def delete_user(self, user_id):
        """
        ISSUE: No authorization check
        ISSUE: No error handling
        """
        del self.users[user_id]
        return {"status": "deleted"}
    
    def search_users(self, query):
        """
        ISSUE: No input sanitization
        ISSUE: Potential injection vulnerability
        """
        # ISSUE: Using eval on user input (CRITICAL SECURITY ISSUE)
        results = [u for u in self.users.values() if eval(query)]
        return results
    
    def export_users(self, format="json"):
        """
        ISSUE: No format validation
        ISSUE: No error handling
        """
        if format == "json":
            return json.dumps(self.users)
        elif format == "csv":
            # ISSUE: Incomplete implementation
            pass


def authenticate_user(username, password):
    """
    ISSUE: Weak authentication logic
    ISSUE: No password hashing
    ISSUE: Hardcoded credentials
    """
    # ISSUE: Credentials in code (CRITICAL)
    if username == "admin" and password == "admin123":
        return True
    return False


def process_payment(card_number, amount, cvv):
    """
    ISSUE: No input validation
    ISSUE: No error handling
    ISSUE: Sensitive data in logs
    """
    # ISSUE: Logging sensitive data
    print(f"Processing payment: Card {card_number}, CVV {cvv}, Amount {amount}")
    
    # ISSUE: No validation of card number format
    # ISSUE: No validation of amount
    # ISSUE: No error handling for payment gateway
    
    return {"status": "success", "transaction_id": "12345"}


# ISSUE: Function without tests
def generate_api_key(user_id):
    """Generate API key for user."""
    # ISSUE: Weak key generation
    return f"key_{user_id}_12345"


# ISSUE: Function without tests  
def validate_api_key(api_key):
    """Validate API key."""
    # ISSUE: No actual validation logic
    return True