import React from "react";
import { NavLink } from "react-router-dom";

function Header() {
  return (
    <div className=" text-center mx-auto  w-full z-50 sticky bg-white">
      <navbar className="flex flex-row items-center justify-between p-2 lg:p-4 lg:px-10 shadow-lg">
        <NavLink
          to="/"
          className="flex items-center justify-between mb-4 gap-5"
        >
          <img src="/logo_new.jpg" alt="logo" className="w-28 lg:w-56 lg:h-20" />
        </NavLink>
        <div className="flex justify-center items-center gap-10 ">
          <NavLink to="/" className="lg:text-2xl font-bold text-gray-800 hover:text-orange-400">
            Home
          </NavLink>
          <NavLink to="/" className="lg:text-2xl font-bold text-gray-800 hover:text-orange-400">
            Contact
          </NavLink>
          <NavLink to="/" className="lg:text-2xl font-bold text-gray-800 hover:text-orange-400">
            About
          </NavLink>
        </div>
      </navbar>
    </div>
  );
}

export default Header;
