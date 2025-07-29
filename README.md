# HotHawkersInYourArea
## Description
A smart AI-driven video analytics system for monitoring people flow, estimating dwell times in food queue zones, and predicting future queue behavior using LSTM neural networks.

"Hot Hawkers in Your Area" revolutionizes hawker centres with Hawker 2.0, blending computer vision and advanced app frameworks to create smart, efficient, and customer-focused dining spaces.

## Motivation
This project addresses the need for efficient and accurate monitoring of people flow and space usage in real time. By combining AI-powered object detection with a reliable backend, it helps businesses and venues optimize occupancy, improve safety, and enhance user experience—all through automated data collection and analysis.

## 📌 Overview
This project combines real-time object detection, zone-based tracking, and deep learning prediction to help canteens or cafeterias understand crowd patterns and optimize operations.

It consists of:

1. CanteenAnalyzer: Uses YOLO and Supervision to detect and track people in food and seating zones in video footage. It records:

    - Dwell times in queue zones (e.g., "Chicken Rice").

    - Occupancy counts in seating zones (e.g., "Aisle 1").

    - Sends data to a backend API for real-time visualization or dashboard integration.

2. DwellTimePredictor: An LSTM-based model that learns historical dwell time trends and predicts customer queue durations for the next hour using temporal and cyclical features.

## 🛠️ Tech Stack
| 🔧 Component         | 🛠️ Technology Used                                                  |
|---------------------|----------------------------------------------------------------------|
| 🧠 Object Detection  | YOLOv8 (via Ultralytics)                                             |
| 🎥 Tracking / Annotation | Supervision + ByteTrack                                      |
| 📉 Forecasting       | LSTM (TensorFlow / Keras)                                           |
| 🔗 API              | HTTP Requests to Flask backend                                      |
| 🔐 Logging           | Python `logging` module                                             |
| 🌐 Frontend          | React (with Next.js) – live dwell time and people count in the queue |
| ⚙️ Backend           | Flask – serves API routes, manages video inference pipeline (dwell time and count), connects and save to database |
| 🗄️ Database          | Firebase Firestore – stores zone-wise people count, dwell time per person, zone capacity status, and timestamps |


## 🧠 Key Features
### 🏷️ Zone-Based People Analytics
- Detects and tracks people entering/leaving polygonal zones.

- Differentiates between food queues (tracks dwell time) and seating areas (counts occupants).

- Maintains identity tracking across frames with ByteTrack.

### 🕒 Dwell Time Tracking
- Assigns dwell time per tracked individual in a queue zone.

- Ignores short dwell durations (e.g., <8 seconds) as noise.

- Posts structured records to /dwelltimes API endpoint.

### 📊 Aisle Occupancy Monitoring
- Periodically counts the number of people in each seating zone.

- Compares live count against seating capacity.

- Posts records to /counts API with occupancy rate (% filled).

### 🔮 LSTM-Based Forecasting
- Predicts dwell times for any store/queue for the next 60 minutes.

- Uses temporal, cyclical (hour/minute sin/cos), and weekday features.

- Saves models in .keras format along with preprocessing scalers and training histories.


## Run the project
For this project, please use two terminals for frontend and backend

### Frontend
```
cd my-app
npm install
npm run dev
```

### Backend
```
cd backend-app
python -m .venv venv
source venv/bin/activate
pip install -r requirement.txt
python app.py
```

### Port
Frontend is accessible at http://10.32.4.205:3000 \
Frontend is exposed at port 5000
