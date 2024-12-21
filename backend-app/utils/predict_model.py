import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import pickle
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

class DwellTimePredictor:
    def __init__(self, save_dir='saved_models'):
        self.save_dir = save_dir
        self.trained_models = {}
        self.seq_length = 30
        
    # [Previous methods remain the same until save_models]
    
    def save_models(self):
        """Save all trained models"""
        os.makedirs(self.save_dir, exist_ok=True)
        
        for store_name, components in self.trained_models.items():
            store_dir = os.path.join(self.save_dir, store_name.replace(' ', '_'))
            os.makedirs(store_dir, exist_ok=True)
            
            # Add .keras extension for model saving
            components['model'].save(os.path.join(store_dir, 'lstm_model.keras'))
            joblib.dump(components['scaler'], os.path.join(store_dir, 'scaler.pkl'))
            components['store_data'].to_pickle(os.path.join(store_dir, 'store_data.pkl'))
            with open(os.path.join(store_dir, 'history.pkl'), 'wb') as f:
                pickle.dump(components['history'].history, f)
        
        print(f"Models saved to {self.save_dir}")
    
    def load_models(self):
        """Load all saved models"""
        if not os.path.exists(self.save_dir):
            raise FileNotFoundError(f"Directory {self.save_dir} not found")
        
        store_dirs = [d for d in os.listdir(self.save_dir) 
                     if os.path.isdir(os.path.join(self.save_dir, d))]
        
        for store_dir in store_dirs:
            store_path = os.path.join(self.save_dir, store_dir)
            store_name = store_dir.replace('_', ' ')
            
            # Load model with .keras extension
            model = load_model(os.path.join(store_path, 'lstm_model.keras'))
            scaler = joblib.load(os.path.join(store_path, 'scaler.pkl'))
            store_data = pd.read_pickle(os.path.join(store_path, 'store_data.pkl'))
            
            with open(os.path.join(store_path, 'history.pkl'), 'rb') as f:
                history = pickle.load(f)
            
            class HistoryWrapper:
                def __init__(self, history_dict):
                    self.history = history_dict
            
            self.trained_models[store_name] = {
                'model': model,
                'scaler': scaler,
                'store_data': store_data,
                'history': HistoryWrapper(history)
            }
        
        print(f"Loaded models for stores: {list(self.trained_models.keys())}")
        
    def create_sequences(self, data, seq_length):
        """Create sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    def prepare_data(self, df, store_name):
        """Prepare data for LSTM model"""
        store_data = df[df['store'] == store_name].copy()
        store_data['timestamp'] = pd.to_datetime(store_data['timestamp'])
        
        # Create features
        store_data['hour'] = store_data['timestamp'].dt.hour
        store_data['minute'] = store_data['timestamp'].dt.minute
        store_data['day_of_week'] = store_data['timestamp'].dt.dayofweek
        
        # Cyclical features
        store_data['hour_sin'] = np.sin(2 * np.pi * store_data['hour']/24)
        store_data['hour_cos'] = np.cos(2 * np.pi * store_data['hour']/24)
        store_data['minute_sin'] = np.sin(2 * np.pi * store_data['minute']/60)
        store_data['minute_cos'] = np.cos(2 * np.pi * store_data['minute']/60)
        
        # One-hot encode day of week
        dow_dummies = pd.get_dummies(store_data['day_of_week'], prefix='dow')
        store_data = pd.concat([store_data, dow_dummies], axis=1)
        
        # Select features
        feature_columns = ['dwell_time', 'hour_sin', 'hour_cos', 'minute_sin', 'minute_cos'] + \
                         [col for col in store_data.columns if col.startswith('dow_')]
        
        # Scale features
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(store_data[feature_columns])
        
        # Create sequences
        X, y = self.create_sequences(scaled_data, self.seq_length)
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        return (X_train, y_train), (X_test, y_test), scaler, store_data
    
    def build_model(self, input_shape):
        """Build LSTM model"""
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_store_model(self, df, store_name):
        """Train model for a specific store"""
        print(f"\nTraining model for {store_name}...")
        (X_train, y_train), (X_test, y_test), scaler, store_data = self.prepare_data(df, store_name)
        
        model = self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        history = model.fit(
            X_train, y_train,
            epochs=10,
            batch_size=32,
            validation_split=0.2,
            verbose=1
        )
        
        self.trained_models[store_name] = {
            'model': model,
            'scaler': scaler,
            'store_data': store_data,
            'history': history
        }
    
    
    def prepare_data(self, df, store_name):
        """Prepare data for LSTM model"""
        store_data = df[df['store'] == store_name].copy()
        
        # Handle timezone conversion safely
        store_data['timestamp'] = pd.to_datetime(store_data['timestamp'])
        if store_data['timestamp'].dt.tz is None:
            store_data['timestamp'] = store_data['timestamp'].dt.tz_localize('UTC')
        else:
            store_data['timestamp'] = store_data['timestamp'].dt.tz_convert('UTC')
        
        # Create features
        store_data['hour'] = store_data['timestamp'].dt.hour
        store_data['minute'] = store_data['timestamp'].dt.minute
        store_data['day_of_week'] = store_data['timestamp'].dt.dayofweek
        
        # Cyclical features
        store_data['hour_sin'] = np.sin(2 * np.pi * store_data['hour']/24)
        store_data['hour_cos'] = np.cos(2 * np.pi * store_data['hour']/24)
        store_data['minute_sin'] = np.sin(2 * np.pi * store_data['minute']/60)
        store_data['minute_cos'] = np.cos(2 * np.pi * store_data['minute']/60)
        
        # Create fixed set of day-of-week dummies
        for i in range(7):
            store_data[f'dow_{i}'] = (store_data['day_of_week'] == i).astype(int)
        
        # Select features in fixed order
        feature_columns = ['dwell_time', 'hour_sin', 'hour_cos', 'minute_sin', 'minute_cos'] + \
                        [f'dow_{i}' for i in range(7)]
        
        # Scale features
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(store_data[feature_columns])
        
        # Create sequences
        X, y = self.create_sequences(scaled_data, self.seq_length)
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        return (X_train, y_train), (X_test, y_test), scaler, store_data

    def predict_next_hour(self, store_name, input_timestamp):
        """Predict dwell times for next hour"""
        if store_name not in self.trained_models:
            raise ValueError(f"No trained model found for {store_name}")
            
        # Standardize timestamp timezone handling
        if isinstance(input_timestamp, str):
            input_timestamp = pd.to_datetime(input_timestamp).tz_localize('UTC')
        elif isinstance(input_timestamp, pd.Timestamp) and input_timestamp.tz is None:
            input_timestamp = input_timestamp.tz_localize('UTC')
        elif isinstance(input_timestamp, pd.Timestamp):
            input_timestamp = input_timestamp.tz_convert('UTC')
        
        components = self.trained_models[store_name]
        model = components['model']
        scaler = components['scaler']
        store_data = components['store_data'].copy()
        
        # Handle timezone conversion safely
        if store_data['timestamp'].dt.tz is None:
            store_data['timestamp'] = store_data['timestamp'].dt.tz_localize('UTC')
        else:
            store_data['timestamp'] = store_data['timestamp'].dt.tz_convert('UTC')
        
        # Generate future timestamps
        future_timestamps = [input_timestamp + pd.Timedelta(minutes=i) for i in range(60)]
        
        # Create prediction DataFrame
        pred_df = pd.DataFrame({'timestamp': future_timestamps})
        pred_df['hour'] = pred_df['timestamp'].dt.hour
        pred_df['minute'] = pred_df['timestamp'].dt.minute
        pred_df['day_of_week'] = pred_df['timestamp'].dt.dayofweek
        
        # Create cyclical features
        pred_df['hour_sin'] = np.sin(2 * np.pi * pred_df['hour']/24)
        pred_df['hour_cos'] = np.cos(2 * np.pi * pred_df['hour']/24)
        pred_df['minute_sin'] = np.sin(2 * np.pi * pred_df['minute']/60)
        pred_df['minute_cos'] = np.cos(2 * np.pi * pred_df['minute']/60)
        
        # Create fixed set of day-of-week dummies
        for i in range(7):
            pred_df[f'dow_{i}'] = (pred_df['day_of_week'] == i).astype(int)
        
        # Get recent data for sequence
        recent_data = store_data[store_data['timestamp'] < input_timestamp].tail(self.seq_length)
        
        if len(recent_data) < self.seq_length:
            raise ValueError("Not enough historical data available")
        
        # Prepare feature columns in same order as training
        feature_columns = ['dwell_time', 'hour_sin', 'hour_cos', 'minute_sin', 'minute_cos'] + \
                        [f'dow_{i}' for i in range(7)]
        
        # Create initial sequence
        initial_sequence = scaler.transform(recent_data[feature_columns])
        
        # Make predictions
        predictions = []
        current_sequence = initial_sequence.copy()
        
        for i in range(60):
            X = current_sequence.reshape(1, self.seq_length, len(feature_columns))
            pred = model.predict(X, verbose=0)
            predictions.append(pred[0][0])
            
            next_features = np.zeros(len(feature_columns))
            next_features[0] = pred[0][0]
            next_features[1:5] = [
                pred_df.iloc[i]['hour_sin'],
                pred_df.iloc[i]['hour_cos'],
                pred_df.iloc[i]['minute_sin'],
                pred_df.iloc[i]['minute_cos']
            ]
            for j in range(7):
                next_features[5+j] = pred_df.iloc[i][f'dow_{j}']
            
            current_sequence = np.vstack([current_sequence[1:], next_features])
        
        # Scale back predictions
        dummy = np.zeros((len(predictions), scaler.scale_.shape[0]))
        dummy[:, 0] = predictions
        predictions_unscaled = scaler.inverse_transform(dummy)[:, 0]
        
        # Create results DataFrame
        results = pd.DataFrame({
            'timestamp': future_timestamps,
            'predicted_dwell_time': predictions_unscaled
        })
    
        return results
    
    def plot_predictions(self, predictions_df, store_name):
        """Plot predicted dwell times"""
        plt.figure(figsize=(12, 6))
        plt.plot(predictions_df['timestamp'], predictions_df['predicted_dwell_time'], 
                 marker='o', linestyle='-', markersize=4)
        plt.title(f"Predicted Dwell Times for {store_name}")
        plt.xlabel("Time")
        plt.ylabel("Predicted Dwell Time (minutes)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()