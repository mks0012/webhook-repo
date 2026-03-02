from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.github_actions
collection = db.events


try:
    client.admin.command('ping')
    print("✅ SUCCESS: Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ ERROR: MongoDB Connection Failed: {e}")

def format_timestamp(dt):
    
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = dt.astimezone(timezone(ist_offset))
    
    day = ist_time.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    
    
    return ist_time.strftime(f"{day}{suffix} %B %Y - %I:%M %p IST")

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "ping":
        return jsonify({"status": "ping received"}), 200
    
    event_doc = {
        "author": "",
        "action": "",
        "from_branch": "",
        "to_branch": "",
        "request_id": "",
        "timestamp": format_timestamp(datetime.now(timezone.utc)) # Modern UTC call
    }

    try:
        if event_type == "push":
            event_doc["action"] = "PUSH"
            event_doc["author"] = data.get('pusher', {}).get('name', 'unknown')
            event_doc["to_branch"] = data.get('ref', '').split('/')[-1]
            event_doc["request_id"] = data.get('after', '')
            
        elif event_type == "pull_request":
            pr = data.get('pull_request', {})
            is_merged = pr.get('merged', False)
            action = data.get('action')

            if action == "closed" and is_merged:
                event_doc["action"] = "MERGE"
                event_doc["author"] = pr.get('merged_by', {}).get('login', 'unknown')
            else:
                event_doc["action"] = "PULL_REQUEST"
                event_doc["author"] = pr.get('user', {}).get('login', 'unknown')

            event_doc["request_id"] = str(pr.get('id', ''))
            event_doc["from_branch"] = pr.get('head', {}).get('ref', '')
            event_doc["to_branch"] = pr.get('base', {}).get('ref', '')

        if event_doc["action"]:
            collection.insert_one(event_doc)
            resp = jsonify({"status": "success"})
            resp.headers.add("ngrok-skip-browser-warning", "true")
            return resp, 200

    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ignored"}), 200

@app.route('/api/actions', methods=['GET'])
def get_actions():
    try:
        
        actions = list(collection.find().sort("_id", -1).limit(10))
        for action in actions:
            action["_id"] = str(action["_id"])
        
        resp = jsonify(actions)
        resp.headers.add("ngrok-skip-browser-warning", "true")
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)