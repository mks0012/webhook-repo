from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.github_actions
collection = db.events

def format_timestamp(dt):
    # Requirement: "1st April 2021 - 9:30 PM UTC"
    day = dt.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return dt.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    event_doc = {
        "author": "",
        "action": "",
        "from_branch": "",
        "to_branch": "",
        "request_id": "",
        "timestamp": format_timestamp(datetime.utcnow())
    }

    if event_type == "push":
        event_doc["action"] = "PUSH"
        event_doc["author"] = data['pusher']['name']
        event_doc["to_branch"] = data['ref'].split('/')[-1]
        event_doc["request_id"] = data['after'] # Git commit hash
        
    elif event_type == "pull_request":
        is_merged = data['pull_request'].get('merged', False)
        action = data.get('action')

        # Check for MERGE (Brownie Points)
        if action == "closed" and is_merged:
            event_doc["action"] = "MERGE"
            event_doc["author"] = data['pull_request']['merged_by']['login']
        else:
            event_doc["action"] = "PULL_REQUEST"
            event_doc["author"] = data['pull_request']['user']['login']

        event_doc["request_id"] = str(data['pull_request']['id'])
        event_doc["from_branch"] = data['pull_request']['head']['ref']
        event_doc["to_branch"] = data['pull_request']['base']['ref']

    if event_doc["action"]:
        collection.insert_one(event_doc)
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ignored"}), 200

# Endpoint for UI to poll
@app.route('/api/actions', methods=['GET'])
def get_actions():
    actions = list(collection.find().sort("_id", -1).limit(10))
    for action in actions:
        action["_id"] = str(action["_id"])
    return jsonify(actions)

if __name__ == '__main__':
    app.run(port=5000, debug=True)