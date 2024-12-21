# from datetime import datetime, timezone
# from flask_cors import cross_origin
# from pydantic import BaseModel
# from flask import Blueprint, request, jsonify
# from utils.firebase_config import get_collection
# from utils.predict_model import DwellTimePredictor
# import pytz
# prediction_bp = Blueprint("predict", __name__)


# #Create new instance of data
# @cross_origin(origins="http://localhost:3000")
# @prediction_bp.route('/predict', methods=['POST'])
# def add_data():
#     if request.method == "OPTIONS":
#         return jsonify({"status": "ok"}), 200
#     try:
#         # Get and validate payload
#         data = request.json
#         if not data or 'timestamp' not in data or 'store' not in data:
#             return jsonify({
#                 'error': 'Missing required fields: timestamp and store'
#             }), 400
#         #timestamp = datetime.now(pytz.UTC).isoformat()
#         timestamp = data["timestamp"]  # format "2024-12-22 12:00:00"
#         store_name = data["store"]

#         # Initialize predictor and load models
#         predictor = DwellTimePredictor()
#         predictor.load_models()

#         # Get predictions
#         results = predictor.predict_next_hour(store_name, timestamp)
        
#         # Convert DataFrame to JSON-serializable format
#         predictions = results.to_dict('records')
        
#         # Format timestamps to ISO format for frontend
#         for pred in predictions:
#             pred['timestamp'] = pred['timestamp'].isoformat()

#         return jsonify({
#             'success': True,
#             'predictions': predictions,
#             'store': store_name,
#             'timestamp': timestamp
#         }), 200

#     except ValueError as e:
#         # Handle specific prediction errors
#         return jsonify({
#             'error': str(e),
#             'type': 'ValueError'
#         }), 400
        
#     except Exception as e:
#         # Handle unexpected errors
#         return jsonify({
#             'error': f'An unexpected error occurred: {str(e)}',
#             'type': 'UnexpectedError'
#         }), 500
from datetime import datetime, timezone
from flask_cors import cross_origin
from pydantic import BaseModel
from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection
from utils.predict_model import DwellTimePredictor
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

prediction_bp = Blueprint("predict", __name__)

@cross_origin(origins="http://localhost:3000")
@prediction_bp.route('/predict', methods=['POST'])
def add_data():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    try:
        # Log the incoming request data
        logger.debug(f"Received request with headers: {dict(request.headers)}")
        logger.debug(f"Request content type: {request.content_type}")
        logger.debug(f"Raw request data: {request.get_data()}")
        
        # Get and validate payload
        data = request.json
        logger.debug(f"Parsed JSON data: {data}")
        
        if not data:
            logger.error("No JSON data found in request")
            return jsonify({
                'error': 'No JSON data provided'
            }), 400
            
        # Log specific field checks
        logger.debug(f"'timestamp' in data: {'timestamp' in data}")
        logger.debug(f"'store' in data: {'store' in data}")
        
        if 'timestamp' not in data or 'store' not in data:
            missing_fields = []
            if 'timestamp' not in data:
                missing_fields.append('timestamp')
            if 'store' not in data:
                missing_fields.append('store')
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        timestamp = data["timestamp"]  # format "2024-12-22 12:00:00"
        # timestamp= "2024-12-22T12:00:00.000Z"
        store_name = data["store"]
        
        logger.debug(f"Processing request for store: {store_name} at time: {timestamp}")

        # Initialize predictor and load models
        predictor = DwellTimePredictor()
        logger.debug("Initialized predictor")
        
        predictor.load_models()
        logger.debug("Loaded models successfully")

        # Get predictions
        logger.debug("Starting prediction")
        results = predictor.predict_next_hour(store_name, timestamp)
        logger.debug(f"Prediction results: {results}")
        
        # Convert DataFrame to JSON-serializable format
        predictions = results.to_dict('records')
        logger.debug(f"Converted predictions to dict: {predictions}")
        
        # Format timestamps to ISO format for frontend
        for pred in predictions:
            pred['timestamp'] = pred['timestamp'].isoformat()

        response_data = {
            'success': True,
            'predictions': predictions,
            'store': store_name,
            'timestamp': timestamp
        }
        logger.debug(f"Sending response: {response_data}")
        
        return jsonify(response_data), 200

    except ValueError as e:
        logger.error(f"ValueError occurred: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'type': 'ValueError'
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'type': 'UnexpectedError'
        }), 500

