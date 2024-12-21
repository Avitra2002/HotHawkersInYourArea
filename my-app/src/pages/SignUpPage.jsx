import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignUpPageContext } from '../contexts/SignUpPageContext';

const SignUpPage = () => {
  const {
    name,
    setName,
    email,
    setEmail,
    password,
    setPassword,
  } = useContext(SignUpPageContext);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => setName(e.target.value);
  const handleEmailChange = (e) => setEmail(e.target.value);
  const handlePWChange = (e) => setPassword(e.target.value);

  const handleSubmit = (event) => {
    event.preventDefault();
    setError('');

    if (!name || !email || !password) {
      setError('Please fill out all fields.');
      return;
    }

    // Preferences are already saved in the context
    console.log('User details saved:', {
      name,
      email,
      password,
    });

    // Navigate to another page after submission
    navigate('/preferences');
  };

  return (
    <div>
      <section className="bg-indigo-50">
        <div className="container m-auto max-w-2xl py-24">
          <div className="bg-white px-6 py-8 mb-4 shadow-md rounded-md border m-4 md:m-0">
            <form onSubmit={handleSubmit}>
              <h2 className="text-3xl text-center font-semibold mb-6">Sign Up</h2>

              {error && <p className="text-red-500 text-center mb-4">{error}</p>}

              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  className="border rounded w-full py-2 px-3 mb-2"
                  placeholder="Bob"
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="border rounded w-full py-2 px-3 mb-2"
                  placeholder="someone@example.com"
                  onChange={handleEmailChange}
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  className="border rounded w-full py-2 px-3"
                  placeholder="Password"
                  onChange={handlePWChange}
                  required
                />
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
    </div>
  );
};

export default SignUpPage;
