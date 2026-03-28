"""
Main application file with intentional code quality issues.
Issues: High complexity, missing error handling, hardcoded credentials
"""

import os
import sqlite3

# ISSUE: Hardcoded credentials (CRITICAL)
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

def process_user_data(user_id, action, data, options=None, validate=True, log=True, retry=False):
    """
    ISSUE: High cyclomatic complexity (>10 branches)
    ISSUE: Missing error handling
    ISSUE: No input validation
    """
    if action == "create":
        if validate:
            if data:
                if "email" in data:
                    if "@" in data["email"]:
                        if log:
                            print(f"Creating user {user_id}")
                        # ISSUE: SQL injection vulnerability
                        query = f"INSERT INTO users VALUES ('{user_id}', '{data['email']}')"
                        conn = sqlite3.connect("users.db")  # ISSUE: No try-except
                        conn.execute(query)
                        conn.commit()
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    elif action == "update":
        if data:
            if user_id:
                if validate:
                    if log:
                        print(f"Updating user {user_id}")
                    # ISSUE: SQL injection vulnerability
                    query = f"UPDATE users SET email='{data['email']}' WHERE id='{user_id}'"
                    conn = sqlite3.connect("users.db")
                    conn.execute(query)
                    conn.commit()
                    return True
    elif action == "delete":
        if user_id:
            if log:
                print(f"Deleting user {user_id}")
            query = f"DELETE FROM users WHERE id='{user_id}'"
            conn = sqlite3.connect("users.db")
            conn.execute(query)
            conn.commit()
            return True
    return False


def calculate_discount(price, user_type, coupon_code, is_premium, is_first_purchase):
    """
    ISSUE: High complexity
    ISSUE: No docstring explaining parameters
    ISSUE: No input validation
    """
    discount = 0
    if user_type == "premium":
        if is_premium:
            discount = 0.2
            if is_first_purchase:
                discount = 0.3
                if coupon_code:
                    if coupon_code == "WELCOME":
                        discount = 0.4
                    elif coupon_code == "SPECIAL":
                        discount = 0.5
    elif user_type == "regular":
        if is_first_purchase:
            discount = 0.1
            if coupon_code:
                if coupon_code == "FIRST10":
                    discount = 0.15
    
    final_price = price * (1 - discount)
    return final_price


def send_notification(user_id, message):
    """
    ISSUE: Missing error handling for network operations
    ISSUE: No retry logic
    """
    # Simulated API call
    api_url = f"https://api.example.com/notify/{user_id}"
    # ISSUE: No try-except for network call
    response = os.system(f"curl -X POST {api_url}")
    return response


# ISSUE: Function without any tests
def generate_report(start_date, end_date, format="pdf"):
    """Generate sales report for date range."""
    # ISSUE: No date validation
    # ISSUE: No format validation
    report_data = f"Report from {start_date} to {end_date}"
    return report_data


if __name__ == "__main__":
    # ISSUE: No error handling in main
    result = process_user_data(
        user_id="123",
        action="create",
        data={"email": "test@example.com"}
    )
    print(f"Result: {result}")