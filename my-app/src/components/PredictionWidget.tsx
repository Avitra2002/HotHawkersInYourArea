import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Define interfaces for our data types
interface Prediction {
  timestamp: string;
  predicted_dwell_time: number;
}

interface PredictionResponse {
  success: boolean;
  predictions: Prediction[];
  store: string;
  timestamp: string;
}

const PredictionWidget: React.FC = () => {
  const [selectedStore, setSelectedStore] = useState<string>('Chicken Rice');
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const stores = ['Chicken Rice', 'Indian', 'Taiwanese'];

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const currentTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
      
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timestamp: currentTime,
          store: selectedStore
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch predictions');
      }

      const data: PredictionResponse = await response.json();
      setPredictions(data.predictions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [selectedStore]);

  const chartData = predictions.map(pred => ({
    time: new Date(pred.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    }),
    dwell: parseFloat(pred.predicted_dwell_time.toFixed(1))
  }));

  return (
    <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">
          Predicted Q time in the next Hour from now
        </h2>
        <div className="w-48">
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          >
            {stores.map(store => (
              <option key={store} value={store}>
                {store}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      )}

      {error && (
        <div className="text-red-500 text-center p-4">
          Error: {error}
        </div>
      )}

      {!loading && !error && (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 10,
                right: 30,
                left: 20,
                bottom: 30
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                angle={-45} 
                textAnchor="end" 
                height={60}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                label={{ 
                  value: 'Queue Time (minutes)', 
                  angle: -90, 
                  position: 'insideLeft',
                  offset: 0,
                  style: { textAnchor: 'middle' }
                }}
                domain={[0, 'auto']}
              />
              <Tooltip
                formatter={(value: number) => [`${value} minutes`, 'Queue Time']}
                labelFormatter={(label: string) => `Time: ${label}`}
              />
              <Legend verticalAlign="top" height={36} />
              <Line
                type="monotone"
                dataKey="dwell"
                name="Predicted Queue Time"
                stroke="#4f46e5"
                strokeWidth={2}
                dot={{ r: 2 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="text-sm text-gray-500 mt-4 text-right">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default PredictionWidget;