from datetime import datetime, timezone
from pydantic import BaseModel
from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection

test_bp = Blueprint("test", __name__)

class TestSchema(BaseModel):
    count: int
    name: str

#Create new instance of data
@test_bp.route('/test', methods=['POST'])
def add_data():
    try:
        # Get the current timestamp
        timestamp = datetime.now(timezone.utc)

        # Receive data as JSON and add timestamp
        data = request.json
        data = TestSchema(**data).model_dump()
        data['timestamp'] = timestamp

        # Save to Firestore
        collection = get_collection('test')
        doc_ref = collection.add(data)
        return jsonify({"success": True, "doc_id": doc_ref[1].id, "timestamp": timestamp}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

#Get all the test data
@test_bp.route('/test', methods=['GET'])
def get_data():
    try:
        collection = get_collection('test')
        docs = collection.stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400