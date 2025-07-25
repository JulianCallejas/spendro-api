#!/usr/bin/env python3

from app.schemas.transaction import TransactionUpdate
import json

# Test the TransactionUpdate schema with a date string
test_data = {
    "date": "2025-07-24"
}

try:
    transaction_update = TransactionUpdate(**test_data)
    print("Success! Schema validation passed.")
    print(f"Parsed date: {transaction_update.date}")
    print(f"Date type: {type(transaction_update.date)}")
except Exception as e:
    print(f"Error: {e}")

# Test with None
test_data_none = {
    "date": None
}

try:
    transaction_update_none = TransactionUpdate(**test_data_none)
    print("Success! None validation passed.")
    print(f"Parsed date: {transaction_update_none.date}")
except Exception as e:
    print(f"Error with None: {e}")

# Test with empty dict (all optional fields)
try:
    transaction_update_empty = TransactionUpdate()
    print("Success! Empty validation passed.")
    print(f"Default date: {transaction_update_empty.date}")
except Exception as e:
    print(f"Error with empty: {e}")