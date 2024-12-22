import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FaBars, FaTimes } from 'react-icons/fa'; // Import icons
import logo from "../assets/images/logo.png";

const Navbar = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleNavbar = () => setIsExpanded(!isExpanded);

  const linkClass = ({ isActive }) =>
    isActive
      ? "bg-white text-black hover:bg-blue hover:text-black rounded-md px-3 py-2"
      : "text-white hover:bg-white hover:text-black rounded-md px-3 py-2";

  return (
    <div className="relative">
      {/* Expand/Collapse Button */}
      <button
        className={`bg-black text-white p-2 fixed top-4 ${
          isExpanded ? "left-64 md:left-48" : "left-4"
        } z-50 rounded-md transition-all duration-300 ease-in-out`}
        onClick={toggleNavbar}
      >
        {isExpanded ? <FaTimes size={24} /> : <FaBars size={24} />}
      </button>

      {/* Navbar */}
      <nav
        className={`bg-black h-screen fixed top-0 left-0 transform ${
          isExpanded ? "translate-x-0" : "-translate-x-full"
        } w-64 md:w-48 transition-transform duration-300 ease-in-out z-40`}
        style={{ paddingTop: '3rem' }} // Adjust padding for button space
      >
        <div className="flex flex-col items-center w-full">
          {/* Logo */}
          <NavLink className="flex flex-shrink-0 items-center my-4" to="/">
            <img
              className="h-10 w-auto"
              src={logo}
              alt="HIIYA Logo"
            />
            <span className="text-white text-2xl font-bold ml-2">
              HHIYA
            </span>
          </NavLink>

          {/* Links */}
          <div className="mt-8 flex flex-col space-y-2">
            <NavLink to="/" className={linkClass}>
              Home
            </NavLink>
            <NavLink to="/heatmap" className={linkClass}>
              Heatmap
            </NavLink>
            <NavLink to="/hawkers" className={linkClass}>
              All Stores
            </NavLink>
            <NavLink to="/preferences" className={linkClass}>
              Edit Preferences
            </NavLink>
            <NavLink to='/login' className={linkClass}>
              Log Out
            </NavLink>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Navbar;
