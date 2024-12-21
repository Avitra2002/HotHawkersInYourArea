import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase Admin SDK key
FIREBASE_KEY_PATH = "firebase_key.json"

# Initialize Firebase app
cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_app = firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()

# Example: Reference a collection
def get_collection(collection_name):
    return db.collection(collection_name)
