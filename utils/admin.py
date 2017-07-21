import json

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)
