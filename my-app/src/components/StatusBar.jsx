import React, { useState, useEffect, useContext } from 'react';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const StatusBar = () => {
  const { selectedStore } = useContext(PreferencesContext);
  const [currentCapacity, setCurrentCapacity] = useState(null);

  useEffect(() => {
    if (selectedStore) {
      // Make a GET request to the backend
      fetch('http://127.0.0.1:5000/counts/capacity', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch capacity data');
          }
          return response.json();
        })
        .then((data) => {
          console.log(data);
          setCurrentCapacity(data.overallCapacity); // Example value for testing, replace with `data.capacity` from the API
        })
        .catch((error) => {
          console.error('Error fetching capacity data:', error);
        });
    }
  }, [selectedStore]);

  // Function to determine the color based on capacity percentage
  const getCapacityColor = () => {
    if (currentCapacity <= 40) {
      return 'bg-green-500';
    } else if (currentCapacity <= 80) {
      return 'bg-yellow-500';
    } else {
      return 'bg-red-500';
    }
  };

  return (
    <section className="py-4">
      <div className="container-xl lg:container mx-auto">
        <div className="grid grid-cols-1 gap-4 p-4 rounded-lg place-items-center">
          <div className="bg-gray-100 p-4 shadow-md w-[90%] mx-auto rounded-lg lg:w-[90%]">
            <div className="my-4 text-center">
              <h3 className="text-lg font-bold mb-4">Current Capacity</h3>
              {currentCapacity !== null ? (
                <div className="w-full bg-gray-300 rounded-full h-6 relative">
                  <div
                    className={`${getCapacityColor()} h-6 rounded-full text-black font-bold flex items-center justify-center`}
                    style={{ width: `${currentCapacity}%` }}
                  >
                    <span className="absolute inset-0 flex items-center justify-center">
                      {`${currentCapacity}%`}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="w-full flex items-center justify-center h-6">
                  <span>Loading capacity...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StatusBar;
