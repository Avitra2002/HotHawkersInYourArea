from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection

counts_bp = Blueprint("counts", __name__)

#Create new instance of data
@counts_bp.route('/counts', methods=['POST'])
def add_data():
    try:
        data = request.json  # Receive data as JSON
        collection = get_collection('counts')
        doc_ref = collection.add(data)
        return jsonify({"success": True, "doc_id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

#Get all the test data
@counts_bp.route('/counts', methods=['GET'])
def get_data():
    try:
        collection = get_collection('counts')
        docs = collection.stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400