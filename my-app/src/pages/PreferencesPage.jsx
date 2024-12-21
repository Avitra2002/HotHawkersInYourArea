import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const PreferencesPage = () => {
  const {
    selectedCanteen,
    setSelectedCanteen,
    selectedStore,
    setSelectedStore,
    lunchTime,
    setLunchTime,
    dinnerTime,
    setDinnerTime,
  } = useContext(PreferencesContext);

  const navigate = useNavigate();

  const canteenStores = {
    'SUTD Canteen': ['Taiwanese', 'Chicken Rice', 'Indian'],
    'Woodleigh Village Hawker Centre': ['Bak Kut Teh', 'Laksa', 'Fishball Noodles'],
    'North Spine Koufu': ['Japanese Cuisine', 'Korean BBQ', 'Thai Food'],
  };

  const handleCanteenChange = (event) => {
    const selected = event.target.value;
    setSelectedCanteen(selected);
    setSelectedStore(''); // Reset the store when the canteen changes
  };

  const handleStoreChange = (event) => {
    setSelectedStore(event.target.value);
  };

  const handleLunchChange = (event) => {
    setLunchTime(event.target.value);
  };

  const handleDinnerChange = (event) => {
    setDinnerTime(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!selectedCanteen || !selectedStore || !lunchTime || !dinnerTime) {
      alert('Please fill out all fields.');
      return;
    }

    console.log('Preferences saved in context:', {
      selectedCanteen,
      selectedStore,
      lunchTime,
      dinnerTime,
    });

    navigate('/');
  };

  const stores = canteenStores[selectedCanteen] || [];

  return (
    <section className="bg-indigo-50">
      <div className="container m-auto max-w-2xl py-24">
        <div className="bg-white px-6 py-8 mb-4 shadow-md rounded-md border m-4 md:m-0">
          <form onSubmit={handleSubmit}>
            <h2 className="text-3xl text-center font-semibold mb-6">Preferences</h2>

            <div className="mb-4">
              <label htmlFor="canteen" className="block text-gray-700 font-bold mb-2">
                Canteen Name
              </label>
              <select
                id="canteen"
                name="canteen"
                className="border rounded w-full py-2 px-3"
                value={selectedCanteen}
                onChange={handleCanteenChange}
                required
              >
                <option value="" disabled>
                  Select a canteen
                </option>
                {Object.keys(canteenStores).map((canteen) => (
                  <option key={canteen} value={canteen}>
                    {canteen}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label htmlFor="store" className="block text-gray-700 font-bold mb-2">
                Preferred Store
              </label>
              <select
                id="store"
                name="store"
                className="border rounded w-full py-2 px-3"
                value={selectedStore}
                onChange={handleStoreChange}
                required
                disabled={!stores.length}
              >
                <option value="" disabled>
                  {stores.length ? 'Select a store' : 'No stores available'}
                </option>
                {stores.map((store) => (
                  <option key={store} value={store}>
                    {store}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label htmlFor="lunch-time" className="block text-gray-700 font-bold mb-2">
                Lunch Timing
              </label>
              <select
                id="lunch-time"
                name="lunch-time"
                className="border rounded w-full py-2 px-3"
                value={lunchTime}
                onChange={handleLunchChange}
                required
              >
                <option value="" disabled>
                  Select a lunch time
                </option>
                {['12:00 PM - 1:00 PM', '1:00 PM - 2:00 PM', '2:00 PM - 3:00 PM'].map((time) => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label htmlFor="dinner-time" className="block text-gray-700 font-bold mb-2">
                Dinner Timing
              </label>
              <select
                id="dinner-time"
                name="dinner-time"
                className="border rounded w-full py-2 px-3"
                value={dinnerTime}
                onChange={handleDinnerChange}
                required
              >
                <option value="" disabled>
                  Select a dinner time
                </option>
                {['6:00 PM - 7:00 PM', '7:00 PM - 8:00 PM', '8:00 PM - 9:00 PM'].map((time) => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <button
                className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-2 px-4 rounded-full w-full focus:outline-none focus:shadow-outline"
                type="submit"
              >
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};

export default PreferencesPage;
