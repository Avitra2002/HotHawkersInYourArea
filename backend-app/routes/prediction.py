from datetime import datetime, timezone
from pydantic import BaseModel
from flask import Blueprint, request, jsonify
from utils.firebase_config import get_collection
from utils.predict_model import DwellTimePredictor

prediction_bp = Blueprint("predict", __name__)


#Create new instance of data
@prediction_bp.route('/predict', methods=['GET'])
def add_data():
    try:
        # Get and validate payload
        data = request.json
        if not data or 'timestamp' not in data or 'store' not in data:
            return jsonify({
                'error': 'Missing required fields: timestamp and store'
            }), 400

        timestamp = data["timestamp"]  # format "2024-12-22 12:00:00"
        store_name = data["store"]

        # Initialize predictor and load models
        predictor = DwellTimePredictor()
        predictor.load_models()

        # Get predictions
        results = predictor.predict_next_hour(store_name, timestamp)
        
        # Convert DataFrame to JSON-serializable format
        predictions = results.to_dict('records')
        
        # Format timestamps to ISO format for frontend
        for pred in predictions:
            pred['timestamp'] = pred['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'predictions': predictions,
            'store': store_name,
            'timestamp': timestamp
        }), 200

    except ValueError as e:
        # Handle specific prediction errors
        return jsonify({
            'error': str(e),
            'type': 'ValueError'
        }), 400
        
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'type': 'UnexpectedError'
        }), 500


