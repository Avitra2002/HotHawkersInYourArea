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


from flask import jsonify
from datetime import datetime

@counts_bp.route('/counts/capacity', methods=['GET'])
def get_capacity():
    try:
        # Fetch the collection from Firestore
        collection = get_collection('counts')
        docs = collection.stream()

        # Initialize a dictionary to store the latest status for each zone
        latest_zone_data = {}
        total_count = 0
        total_capacity = 0

        # Process each document to extract the latest data for each zone
        for doc in docs:
            record = doc.to_dict()

            # Assuming the document has the following fields:
            # - "zone" (name of the zone)
            # - "timestamp" (timestamp when the count was recorded)
            # - "current_count" (the current count of people in the zone)
            # - "capacity" (the total capacity of the zone)

            zone = record.get('zone')
            timestamp_str = record.get('timestamp')  # Assuming timestamp is in ISO format
            current_count = record.get('current_count', 0)
            capacity = record.get('capacity', 0)
            status = record.get('status', 0)

            if zone and timestamp_str and current_count is not None and capacity is not None:
                # Parse the timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except ValueError:
                    continue  # Skip if timestamp is invalid

                # Check if this is the latest data for the zone
                if zone not in latest_zone_data or timestamp > latest_zone_data[zone]["timestamp"]:
                    # Update the latest data for this zone
                    latest_zone_data[zone] = {
                        "timestamp": timestamp,
                        "current_count": current_count,
                        "capacity": capacity,
                        "status": status
                    }
                    
        # Update the overall count and capacity
        total_count = sum(data["current_count"] for data in latest_zone_data.values())
        total_capacity = sum(data["capacity"] for data in latest_zone_data.values())
        overall_capacity = round((total_count / total_capacity) * 100, 0) if total_capacity else 0

        # Prepare the final result where each zone is a key with the latest status as the value
        result = {
            zone: data["status"]  # Set zone name as the key and status as the value
            for zone, data in latest_zone_data.items()
        }

        # Include the overall capacity in the result
        result["overallCapacity"] = overall_capacity

        # Return the result as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
