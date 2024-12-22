// import React, { useState, useEffect, useContext } from 'react'
// import HawkerListing from './HawkerListing'
// import Spinner from './Spinner'
// import { PreferencesContext } from '../Contexts/PreferencesContext';

// const HawkerListings = ({ isHome = false }) => {
//   const { selectedStore } = useContext(PreferencesContext);
//   const [stores, setStores] = useState([])
//   const [loading, setLoading] = useState(true)

//   useEffect(() => {
//       if (selectedStore) {
//         // Make a POST request to the backend
//         fetch('http://127.0.0.1:5000/dwelltimes/average', {
//           method: 'GET',
//           headers: {
//             'Content-Type': 'application/json',
//           },
//         })
//           .then((response) => {
//             if (!response.ok) {
//               throw new Error('Failed to fetch wait times');
//             }
//             return response.json();
//           })
//           .then((data) => {
//             // Update state with the fetched data
//             console.log(data)
//             setStores(data);
//             setLoading(false);
//           })
//           .catch((error) => {
//             console.error('Error fetching wait times:', error);
//           });
//       }
//     }, [selectedStore]);

//   return (
//     <section className="bg-blue-50 px-4 py-10">
//       <div className="container-xl lg:container m-auto">
//         <h2 className="text-3xl font-bold text-indigo-500 mb-6 text-center">
//           {isHome ? "Other Stores" : "All Stores"}
//         </h2>
//           {loading ? (<Spinner />) : (
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//               {stores.map((store) => (
//                 <HawkerListing key={store.storeNames} store={store} />
//               ))}
//             </div>
//           )}
//       </div>
//     </section>
//   )
// }

// export default HawkerListings
import React, { useState, useEffect, useContext } from 'react';
import HawkerListing from './HawkerListing';
import Spinner from './Spinner';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const HawkerListings = ({ isHome = false }) => {
  const { selectedStore } = useContext(PreferencesContext);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchStoresData = () => {
    if (selectedStore) {
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
          console.log(data);
          setStores(data);
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching wait times:', error);
        });
    }
  };

  useEffect(() => {
    fetchStoresData(); // Fetch data initially

    const interval = setInterval(() => {
      fetchStoresData(); // Fetch data every 30 seconds
    }, 30000);

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, [selectedStore]); // Dependency array ensures it runs when `selectedStore` changes

  return (
    <section className="bg-blue-50 px-4 py-10">
      <div className="container-xl lg:container m-auto">
        <h2 className="text-3xl font-bold text-indigo-500 mb-6 text-center">
          {isHome ? 'Other Stores' : 'All Stores'}
        </h2>
        {loading ? (
          <Spinner />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stores.map((store) => (
              <HawkerListing key={store.storeNames} store={store} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default HawkerListings;
