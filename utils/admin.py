import json

def load_credentials():
    """Load credentials as JSON"""
    with open('credentials.json') as f:
        return json.load(f)
