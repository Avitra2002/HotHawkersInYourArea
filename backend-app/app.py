from flask import Flask
from flask_cors import CORS
from routes import register_blueprints

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Register all blueprints
register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True)