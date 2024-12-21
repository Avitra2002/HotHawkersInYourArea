from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection
import csv
from datetime import datetime, timedelta, timezone
import pytz  # If your timestamps are timezone-aware

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
    

# @dwelltimes_bp.route('/dwelltimes/addall', methods=['POST'])
# def upload_csv_to_firestore():
#     csv_file_path = "../model/output.csv"
#     try:
#         # Get reference to the Firestore collection
#         collection = get_collection('dwelltimes')
        
#         # Open the CSV file
#         with open(csv_file_path, mode='r') as file:
#             reader = csv.DictReader(file)  # Read as dictionary
            
#             # Iterate through each row and upload to Firestore
#             for row in reader:
#                 # Convert dwell_time to integer (optional)
#                 row['dwell_time'] = int(row['dwell_time'])
                
#                 # Add the row to Firestore
#                 doc_ref = collection.add(row)
#                 print(f"Added document with ID: {doc_ref[1].id}")
        
#         print("CSV data uploaded successfully.")
#         return jsonify({"success": True}), 201
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 400

# @dwelltimes_bp.route('/dwelltimes/average', methods=['GET'])
# def get_average_dwell_times():
#     try:
#         # Fetch the data from the Firestore collection
#         collection = get_collection('dwelltimes')
#         docs = collection.stream()

#         # Initialize a dictionary to aggregate dwell times
#         store_dwell_times = {}

#         # Process each document
#         for doc in docs:
#             record = doc.to_dict()
#             store = record.get('store')
#             dwell_time = record.get('dwell_time', 0)
#             if store:
#                 if store not in store_dwell_times:
#                     store_dwell_times[store] = []
#                 store_dwell_times[store].append(dwell_time)

#         # Compute the average dwell time for each store
#         average_dwell_times = {
#             store: sum(times) / len(times)
#             for store, times in store_dwell_times.items()
#         }

#         # Return the results as JSON
#         return jsonify(average_dwell_times), 200

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 400


@dwelltimes_bp.route('/dwelltimes/average', methods=['GET'])
def get_average_dwell_times():
    try:
        # Get the current timestamp and calculate the threshold (5 minutes ago)
        current_time = datetime.now(timezone.utc).replace(tzinfo=pytz.UTC)
        time_threshold = current_time - timedelta(minutes=5)
        # Fetch the Firestore collection
        collection = get_collection('dwelltimes')

        # Filter documents with timestamps greater than the threshold
        docs = collection.stream()
        # Initialize a dictionary to aggregate dwell times
        store_dwell_times = {}

        # Process each document
        for doc in docs:
            record = doc.to_dict()

            # Parse the string timestamp into a datetime object
            timestamp_str = record.get('timestamp')
            if not timestamp_str:
                continue

            # Convert string timestamp to datetime
            try:
                record_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                continue  # Skip records with invalid timestamp format

            # Check if the record's timestamp is within the threshold
            if record_timestamp >= time_threshold:
                store = record.get('store')
                dwell_time = record.get('dwell_time', 0)
                if store:
                    if store not in store_dwell_times:
                        store_dwell_times[store] = []
                    store_dwell_times[store].append(dwell_time)

        # Compute the average dwell time for each store and format the output
        average_dwell_times = [
            {"store": store, "averageDwellTime": sum(times) / len(times)}
            for store, times in store_dwell_times.items()
        ]

        # Return the results as JSON
        return jsonify(average_dwell_times), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    


@dwelltimes_bp.route('/dwelltimes/average/<string:storename>', methods=['GET'])
def get_average_dwell_time_for_store(storename):
    try:
        # Get the current timestamp and calculate the threshold (5 minutes ago)
        current_time = datetime.now(timezone.utc).replace(tzinfo=pytz.UTC)
        #current_time = current_time - timedelta(minutes=300)
        time_threshold = current_time - timedelta(minutes=5)

        # Fetch the Firestore collection
        collection = get_collection('dwelltimes')
        docs = collection.stream()

        # Initialize a list to store dwell times for the specific store
        dwell_times = []

        # Process each document
        for doc in docs:
            record = doc.to_dict()

            # Parse the string timestamp into a datetime object
            timestamp_str = record.get('timestamp')
            if not timestamp_str:
                continue

            # Convert string timestamp to datetime
            try:
                record_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                continue  # Skip records with invalid timestamp format

            # Check if the record's timestamp is within the threshold
            if record_timestamp >= time_threshold:
                store = record.get('store')
                dwell_time = record.get('dwell_time', 0)
                if store == storename:
                    dwell_times.append(dwell_time)

        # Compute the average dwell time for the specified store
        if dwell_times:
            average_dwell_time = sum(dwell_times) / len(dwell_times)
            result = {"store": storename, "averageDwellTime": average_dwell_time}
        else:
            result = {"store": storename, "averageDwellTime": None, "message": "No recent data found"}

        # Return the results as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
