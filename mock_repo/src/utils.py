"""
Utility functions with code quality issues.
Issues: Code duplication, missing docstrings, no error handling
"""

def validate_email(email):
    # ISSUE: No docstring
    # ISSUE: Weak validation logic
    if "@" in email and "." in email:
        return True
    return False


def validate_phone(phone):
    # ISSUE: No docstring
    # ISSUE: Code duplication with validate_email pattern
    if len(phone) >= 10:
        return True
    return False


def validate_username(username):
    # ISSUE: No docstring
    # ISSUE: Code duplication with same pattern
    if len(username) >= 3:
        return True
    return False


# ISSUE: Code duplication - same logic repeated
def format_user_data(user):
    result = {}
    if "name" in user:
        result["name"] = user["name"].strip().title()
    if "email" in user:
        result["email"] = user["email"].strip().lower()
    if "phone" in user:
        result["phone"] = user["phone"].strip()
    return result


def format_product_data(product):
    # ISSUE: Exact same logic as format_user_data
    result = {}
    if "name" in product:
        result["name"] = product["name"].strip().title()
    if "email" in product:
        result["email"] = product["email"].strip().lower()
    if "phone" in product:
        result["phone"] = product["phone"].strip()
    return result


def read_config_file(filepath):
    """
    ISSUE: No error handling for file operations
    ISSUE: File not closed properly
    """
    file = open(filepath, 'r')  # ISSUE: No try-except, no with statement
    content = file.read()
    return content


def write_log(message, filepath="app.log"):
    """
    ISSUE: No error handling
    ISSUE: File not closed properly
    """
    file = open(filepath, 'a')
    file.write(message + "\n")
    # ISSUE: File never closed


# ISSUE: Function without tests
def calculate_tax(amount, tax_rate=0.18):
    return amount * tax_rate


# ISSUE: Function without tests
def apply_discount(price, discount_percent):
    return price * (1 - discount_percent / 100)