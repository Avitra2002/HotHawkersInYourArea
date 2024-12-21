import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const Widget = () => {
  const [preferredStore, setPreferredStore] = useState(null);
  const [currentWaitTime, setCurrentWaitTime] = useState(null);
  const [predictedWaitTime, setPredictedWaitTime] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [currentCapacity, setCurrentCapacity] = useState(null); // New state for capacity

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       console.log("fetching data")
  //       const response = await fetch('http://127.0.0.1:5000/preferences/qYEc9Y0mFZVETP6wbIH2');
  //       if (!response.ok) {
  //         throw new Error(`HTTP error! Status: ${response.status}`);
  //       }
  //       const data = await response.json();
  //       console.log(data)
  //       setPreferredStore(data.stores);
  //       setCurrentWaitTime(data.currentWaitTime);
  //       setPredictedWaitTime(data.predictedWaitTime);
  //       setTimeSeriesData(data.timeSeriesData);
  //       setCurrentCapacity(data.currentCapacity); // Fetch capacity from backend
  //     } catch (error) {
  //       console.error('Error fetching data:', error);
  //     }
  //   };

  //   fetchData();
  // }, []);

  // const chartData = {
  //   labels: timeSeriesData.map((dataPoint) => dataPoint.time),
  //   datasets: [
  //     {
  //       label: 'Wait Time (minutes)',
  //       data: timeSeriesData.map((dataPoint) => dataPoint.value),
  //       borderColor: 'rgba(75, 192, 192, 1)',
  //       backgroundColor: 'rgba(75, 192, 192, 0.2)',
  //       tension: 0.4,
  //     },
  //   ],
  // };

  // const options = {
  //   responsive: true,
  //   plugins: {
  //     legend: {
  //       display: true,
  //       position: 'top',
  //     },
  //   },
  //   scales: {
  //     x: {
  //       title: {
  //         display: true,
  //         text: 'Time',
  //       },
  //     },
  //     y: {
  //       title: {
  //         display: true,
  //         text: 'Wait Time (minutes)',
  //       },
  //     },
  //   },
  // };

  return (
    <section className="py-4">
      <div className="container-xl lg:container m-auto">
        <div className="grid grid-cols-1 gap-4 p-4 rounded-lg place-items-center">
          <div className="bg-gray-100 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold">{preferredStore || 'Loading...'}</h2>
            <br />
            <p className="mb-2">Current Wait Time: {currentWaitTime || 'Loading...'}</p>
            <p className="mb-4">Predicted Wait Time: {predictedWaitTime || 'Loading...'}</p>
            {/* <div className="my-4">
              {timeSeriesData.length ? (
                <Line data={chartData} options={options} />
              ) : (
                'Loading time-series data...'
              )}
            </div> */}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Widget;
