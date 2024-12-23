import React, { useEffect, useState, useContext } from 'react';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const Widget = () => {
  const { selectedStore } = useContext(PreferencesContext);
  const [currentWaitTime, setCurrentWaitTime] = useState(null);
  const [predictedWaitTime, setPredictedWaitTime] = useState(null);

  useEffect(() => {
    if (selectedStore) {
      const payload = { store: selectedStore };
      console.log(payload);

      // Make a POST request to the backend
      fetch('http://10.32.4.205:5000/dwelltimes/average', {
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
          setCurrentWaitTime(data.averageDwellTime);
        })
        .catch((error) => {
          console.error('Error fetching wait times:', error);
        });
    }
  }, [selectedStore]);

  return (
    <section className="py-6">
      <div className="container-xl lg:container mx-auto">
        <div className="grid grid-cols-1 gap-4 p-4 rounded-lg place-items-center">
          <div className="bg-gray-100 p-4 shadow-md w-[90%] mx-auto rounded-lg lg:w-[90%]">
            <h2 className="text-2xl font-bold text-center">
              Preferred Store: {selectedStore || 'Loading...'}
            </h2>
            <br />
            <p className="mb-2 text-xl text-center">
              Current Wait Time: {currentWaitTime ? `${currentWaitTime} mins` : 'Loading...'}
            </p>
            {/* <p className="mb-4 text-center">
              Predicted Wait Time: {predictedWaitTime ? `${currentWaitTime} mins` : 'Loading...'}
            </p> */}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Widget;
