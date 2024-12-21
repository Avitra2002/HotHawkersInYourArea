import React, { useEffect, useState, useContext } from 'react';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const Widget = () => {
  const { selectedStore } = useContext(PreferencesContext);
  const [currentWaitTime, setCurrentWaitTime] = useState(null);
  const [predictedWaitTime, setPredictedWaitTime] = useState(null);

  useEffect(() => {
    if (selectedStore) {
      const payload = { store: selectedStore };

      // Make a POST request to the backend
      fetch('https://example.com/api/wait-times', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch wait times');
          }
          return response.json();
        })
        .then((data) => {
          // Update state with the fetched data
          setCurrentWaitTime(data.currentWaitTime);
          setPredictedWaitTime(data.predictedWaitTime);
        })
        .catch((error) => {
          console.error('Error fetching wait times:', error);
        });
    }
  }, [selectedStore]);

  return (
    <section className="py-4">
      <div className="container-xl lg:container m-auto">
        <div className="grid grid-cols-1 gap-4 p-4 rounded-lg place-items-center">
          <div className="bg-gray-100 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold">{selectedStore || 'Loading...'}</h2>
            <br />
            <p className="mb-2">Current Wait Time: {currentWaitTime || 'Loading...'}</p>
            <p className="mb-4">Predicted Wait Time: {predictedWaitTime || 'Loading...'}</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Widget;
