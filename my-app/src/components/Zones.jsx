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
          Zones
        </h2>
          {loading ? (<Spinner />) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {stores.map((store) => (
                <HawkerListing key={store.id} store={store} />
              ))}
            </div>
          )}
      </div>
    </section>
  )
}

export default Zones