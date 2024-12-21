import React, { createContext, useState } from 'react';

export const PreferencesContext = createContext();

export const PreferencesProvider = ({ children }) => {
  const [selectedCanteen, setSelectedCanteen] = useState('');
  const [selectedStore, setSelectedStore] = useState([]);
  const [lunchTime, setLunchTime] = useState('');
  const [dinnerTime, setDinnerTime] = useState('');

  const preferences = {
    selectedCanteen,
    setSelectedCanteen,
    selectedStore,
    setSelectedStore,
    lunchTime,
    setLunchTime,
    dinnerTime,
    setDinnerTime,
  };

  return (
    <PreferencesContext.Provider value={preferences}>
      {children}
    </PreferencesContext.Provider>
  );
};
