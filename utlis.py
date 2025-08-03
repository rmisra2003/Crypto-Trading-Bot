import json
import os

def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)

def save_log(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as f:
        f.write(data + '\n')
