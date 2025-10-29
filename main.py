from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Get API key from environment variable
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

def init_db():
    conn = sqlite3.connect('rfid_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rfid_data
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         data TEXT NOT NULL,
         timestamp TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

def verify_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != API_KEY:
        return False
    return True

@app.route('/rfid', methods=['POST'])
def store_rfid_data():
    if not verify_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401
    
    try:
        # Get the raw data from request
        data = request.get_json(force=True)
        
        # Convert data to string format
        data_str = json.dumps(data)
        
        # Store in database
        conn = sqlite3.connect('rfid_data.db')
        c = conn.cursor()
        c.execute('INSERT INTO rfid_data (data, timestamp) VALUES (?, ?)',
                 (data_str, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Data stored successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/rfid', methods=['GET'])
def get_rfid_data():
    if not verify_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401
    
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Connect to database
        conn = sqlite3.connect('rfid_data.db')
        c = conn.cursor()
        
        # Get total count
        total_count = c.execute('SELECT COUNT(*) FROM rfid_data').fetchone()[0]
        
        # Get paginated data
        rows = c.execute('''
            SELECT id, data, timestamp 
            FROM rfid_data 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
        
        # Format the data
        data = [{
            'id': row[0],
            'data': json.loads(row[1]),
            'timestamp': row[2]
        } for row in rows]
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": data,
            "pagination": {
                "total": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize database when the application starts
init_db()
