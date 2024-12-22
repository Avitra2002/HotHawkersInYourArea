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
            print(f"Document Data: {record}")  # Debugging log

            # Extract fields with safeguards
            zone = record.get('zone')
            timestamp_str = record.get('timestamp')  # Assuming timestamp is in ISO format
            current_count = int(record.get('count', 0))  # Default to 0 if missing
            capacity = int(record.get('capacity', 0))  # Default to 0 if missing
            status = record.get('status', 0)

            if zone and timestamp_str and capacity is not None:
                # Parse the timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except ValueError:
                    print(f"Invalid timestamp: {timestamp_str}")  # Debugging log
                    continue  # Skip invalid timestamps

                # Check if this is the latest data for the zone
                if zone not in latest_zone_data or timestamp > latest_zone_data[zone]["timestamp"]:
                    # Update the latest data for this zone
                    latest_zone_data[zone] = {
                        "timestamp": timestamp,
                        "current_count": current_count,
                        "capacity": capacity,
                        "status": status
                    }

        print(f"Latest Zone Data: {latest_zone_data}")  # Debugging log

        # Calculate total count and capacity
        total_count = sum(data["current_count"] for data in latest_zone_data.values())
        total_capacity = sum(data["capacity"] for data in latest_zone_data.values())
        overall_capacity = round((total_count / total_capacity) * 100, 0) if total_capacity else 0

        print(f"Total Count: {total_count}, Total Capacity: {total_capacity}, Overall Capacity: {overall_capacity}")  # Debugging log

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
        print(f"Error: {str(e)}")  # Debugging log for errors
        return jsonify({"success": False, "error": str(e)}), 400
