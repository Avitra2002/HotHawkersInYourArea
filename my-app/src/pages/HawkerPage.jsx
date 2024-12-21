import React, { useState, useEffect, useContext } from 'react'
import { useParams } from 'react-router-dom'
import { PreferencesContext } from '../Contexts/PreferencesContext'
import Spinner from '../components/Spinner'
import HawkerPageDetails from '../components/HawkerPageDetails'

const HawkerPage = () => {
    const { id } = useParams()
    const { selectedStore } = useContext(PreferencesContext);
    const [stores, setStores] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
          if (selectedStore) {
            // Make a POST request to the backend
            fetch('http://127.0.0.1:5000/dwelltimes/average', {
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
                setStores(data);
                setLoading(false);
              })
              .catch((error) => {
                console.error('Error fetching wait times:', error);
              });
          }
        }, [selectedStore]);

    return (
      <>
      {loading ? (<Spinner />) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stores.map((store) => (
            <HawkerPageDetails key={store.storeNames} store={store} />
          ))}
        </div>
      )}
      </>
    )
}

export default HawkerPage