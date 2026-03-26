"""
Partial test coverage for utils module.
ISSUE: Many functions in utils.py are not tested.
"""

import pytest
from src.utils import validate_email, validate_phone

def test_validate_email_valid():
    """Test email validation with valid email."""
    assert validate_email("test@example.com") == True

def test_validate_email_invalid():
    """Test email validation with invalid email."""
    assert validate_email("invalid") == False

def test_validate_phone_valid():
    """Test phone validation with valid phone."""
    assert validate_phone("1234567890") == True

# ISSUE: Missing tests for:
# - validate_username
# - format_user_data
# - format_product_data
# - read_config_file
# - write_log
# - calculate_tax
# - apply_discount