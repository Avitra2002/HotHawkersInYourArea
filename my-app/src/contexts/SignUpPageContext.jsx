import React, { createContext, useState } from 'react';

export const SignUpPageContext = createContext();

export const SignUpPageProvider = ({ children }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState([]);
  const [password, setPassword] = useState('');

  const userDetails = {
    name,
    setName,
    email,
    setEmail,
    password,
    setPassword,
  };

  return (
    <SignUpPageContext.Provider value={userDetails}>
      {children}
    </SignUpPageContext.Provider>
  );
};
