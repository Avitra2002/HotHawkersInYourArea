import React, { createContext, useState } from 'react';

export const SignUpPageContext = createContext();

export const SignUpPageProvider = ({ children }) => {
  const [name, setName] = useState(null);
  const [email, setEmail] = useState(null);
  const [password, setPassword] = useState(null);

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
