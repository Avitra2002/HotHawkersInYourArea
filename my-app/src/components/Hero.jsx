import React, { useContext } from 'react';
import { PreferencesContext } from '../Contexts/PreferencesContext';
import { SignUpPageContext } from '../contexts/SignUpPageContext';

const Hero = () => {
  const { selectedCanteen } = useContext(PreferencesContext)
  const { name } = useContext(SignUpPageContext)

  return (
    <section className="bg-indigo-700 py-20 mb-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
            Hello {name || 'Guest'},
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
