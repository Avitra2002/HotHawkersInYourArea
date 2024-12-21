from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection

accounts_bp = Blueprint("accounts", __name__)

#Create new instance of data
@accounts_bp.route('/accounts', methods=['POST'])
def add_data():
    try:
        data = request.json  # Receive data as JSON
        collection = get_collection('accounts')
        doc_ref = collection.add(data)
        return jsonify({"success": True, "doc_id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

#Get all the test data
@accounts_bp.route('/accounts', methods=['GET'])
def get_data():
    try:
        collection = get_collection('accounts')
        docs = collection.stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400