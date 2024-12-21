import React, { useContext, useEffect, useState } from 'react';
import { PreferencesContext } from '../Contexts/PreferencesContext';

const Hero = () => {
  const { selectedCanteen } = useContext(PreferencesContext)

  // // Fetch name and location when the component mounts
  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       // Fetch user data for the name (e.g., from your user endpoint)
  //       const userResponse = await fetch('https://your-backend-server.com/api/user');
  //       if (!userResponse.ok) {
  //         throw new Error('Failed to fetch user data');
  //       }
  //       const userData = await userResponse.json();
  //       setName(userData.name);

  //       // Fetch location data (preferences) after submission
  //       const preferencesResponse = await fetch('https://your-backend-server.com/api/preferences');
  //       if (!preferencesResponse.ok) {
  //         throw new Error('Failed to fetch preferences');
  //       }
  //       const preferencesData = await preferencesResponse.json();
  //       setLocation(preferencesData.selectedCanteen || 'Not Set');
  //     } catch (error) {
  //       console.error('Error fetching data:', error);
  //       setName('Guest');
  //       setLocation('Unknown');
  //     }
  //   };

  //   fetchData();
  // }, []); // Empty dependency array means it runs once when the component mounts

  return (
    <section className="bg-indigo-700 py-20 mb-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
            Hello {"hi" || 'Guest'},
          </h1>
          <p className="my-4 text-xl text-white">
            Location: {selectedCanteen || 'Not Set'}
          </p>
        </div>
      </div>
    </section>
  );
};

export default Hero;
