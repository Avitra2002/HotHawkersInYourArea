from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection

dwelltimes_bp = Blueprint("dwelltimes", __name__)

#Create new instance of data
@dwelltimes_bp.route('/dwelltimes', methods=['POST'])
def add_data():
    try:
        data = request.json  # Receive data as JSON
        collection = get_collection('dwelltimes')
        doc_ref = collection.add(data)
        return jsonify({"success": True, "doc_id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

#Get all the test data
@dwelltimes_bp.route('/dwelltimes', methods=['GET'])
def get_data():
    try:
        collection = get_collection('dwelltimes')
        docs = collection.stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400