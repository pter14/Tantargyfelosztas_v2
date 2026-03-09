# app.py
from flask import Flask, send_from_directory, request, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='')

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SAVE_FILE = DATA_DIR / "data_store.json"

DEFAULT_STORE = {
    "subjects": [],
    "classes": [],   # each { class_id, grade (opt), groups: [ ... ] }
    "csr": [],       # optional denormalized list, but UI computes from classes x subjects
    "teachers": []   # each teacher: { teacher_id, name, weekly_hours, assignments: { "<subject>::<class>": hours } }
}

def load_store():
    if SAVE_FILE.exists():
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STORE.copy()

def save_store(store):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/load', methods=['GET'])
def api_load():
    store = load_store()
    return jsonify({"status":"ok", "data": store})

@app.route('/api/save', methods=['POST'])
def api_save():
    payload = request.get_json()
    if not payload:
        return jsonify({"status":"error", "message":"No JSON payload"}), 400
    # Basic validation could be added here
    store = {
        "subjects": payload.get("subjects", []),
        "classes": payload.get("classes", []),
        "csr": payload.get("csr", []),
        "teachers": payload.get("teachers", [])
    }
    save_store(store)
    return jsonify({"status":"ok", "message":"Saved", "summary": {"subjects": len(store["subjects"]), "classes": len(store["classes"]), "teachers": len(store["teachers"])}})

if __name__ == '__main__':
    # dev server
    app.run(debug=True, host='0.0.0.0', port=8000)
