GitHub Activity Monitor
A full-stack application designed to capture, process, and visualize GitHub repository events in real-time. This system utilizes webhooks to listen for specific actions, stores them in a cloud database, and displays them on a polling-based dashboard.

🛠️ Tech Stack
Backend: Flask (Python)

Database: MongoDB Atlas (NoSQL)

Frontend: React

Proxy/Tunnel: Ngrok

🏗️ How It Works
Event Capture: GitHub sends a JSON payload via a Webhook whenever a PUSH or MERGE occurs.

Processing: The Flask backend receives the payload via an Ngrok tunnel, extracts relevant metadata (author, branch, action type), and converts the UTC timestamp to IST.

Persistence: The processed event is stored as a document in a MongoDB Atlas collection.

Visualization: The React frontend polls the backend API every 15 seconds to fetch and display the 10 most recent events without requiring a manual page refresh.

🚀 Setup & Installation
1. Prerequisites
Python 3.x

Node.js & npm

Ngrok installed and authenticated

2. Backend Setup
Navigate to the project root.

Create a .env file and add your MongoDB connection string:

Plaintext

MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/github_actions?appName=Cluster0
Install dependencies and start the server:

Bash

pip install -r requirements.txt
python app.py
3. Frontend Setup
Navigate to the frontend directory.

Install dependencies and start the React app:

Bash

npm install
npm start
4. Webhook Configuration
Start your tunnel: ngrok http 5000.

Copy the Forwarding URL and add it to your GitHub Repository Settings > Webhooks.

Set Content Type to application/json.
