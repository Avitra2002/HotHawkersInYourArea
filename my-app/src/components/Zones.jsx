import React, { useState, useEffect, useContext } from 'react'
import HawkerListing from './HawkerListing'
import Spinner from './Spinner'
import { PreferencesContext } from '../Contexts/PreferencesContext';

const Zones = () => {
  const { selectedStore } = useContext(PreferencesContext);
  const [zones, setZones] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
      if (selectedStore) {
        // Make a POST request to the backend
        fetch('http://127.0.0.1:5000/counts/capacity', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error('Failed to fetch wait times');
            }
            return response.json();
          })
          .then((data) => {
            // Update state with the fetched data
            console.log(data)
            setZones(data);
            setLoading(false);
          })
          .catch((error) => {
            console.error('Error fetching wait times:', error);
          });
      }
    }, [selectedStore]);

  return (
    <section className="bg-blue-50 px-4 py-10">
      <div className="container-xl lg:container m-auto">
        <h2 className="text-3xl font-bold text-indigo-500 mb-6 text-center">
          Zones Capacity
        </h2>
          {loading ? (<Spinner />) : 
          <>
            <div className="flex-1 p-4 bg-blue-100 border border-gray-300 text-center">
              Zone 1: {zones["Zone 1"]}%
            </div>
            <br />
            <div className="flex-1 p-4 bg-green-100 border border-gray-300 text-center">
              Zone 2: {zones["Zone 1"]}%
            </div>
            <br />
            <div className="flex-1 p-4 bg-yellow-100 border border-gray-300 text-center">
              Zone 3: {zones["Zone 1"]}%
            </div>
          </>
          }
      </div>
    </section>
  )
}

export default Zones