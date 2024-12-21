from datetime import datetime, timezone
from pydantic import BaseModel
from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection

preferences_bp = Blueprint("preferences", __name__)


#Create new instance of data
@preferences_bp.route('/preferences', methods=['POST'])
def add_data():
    try:
        # Receive data as JSON and add timestamp
        data = request.json
        # Save to Firestore
        collection = get_collection('preferences')
        doc_ref = collection.add(data)
        return jsonify({"success": True, "doc_id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

#Get all the test data
@preferences_bp.route('/preferences', methods=['GET'])
def get_data():
    try:
        collection = get_collection('preferences')
        docs = collection.stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    
#"qYEc9Y0mFZVETP6wbIH2"
@preferences_bp.route('/preferences/<string:doc_id>', methods=['GET'])
def get_preference(doc_id):
    try:
        collection = get_collection('preferences')
        doc = collection.document(doc_id).get()

        if doc.exists:
            # Return the document's data
            return jsonify(doc.to_dict()), 200
        else:
            # Handle case where document does not exist
            return jsonify({"success": False, "error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400