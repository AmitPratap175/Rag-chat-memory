import React, { useState } from "react";
import { LuBot, LuLifeBuoy, LuMessageSquare } from "react-icons/lu";
import { Link } from "react-router-dom";

function SideBar() {
  const [isActive, setisactive] = useState();

//   const menuItems = ["New Chat", "Support", "New bots", "More"];

   const menuItems = [
    { name: "New Chat", icon: <LuMessageSquare className="mr-2 lg:text-2xl text-xl" color="orange" /> },
    { name: "Support", icon: <LuLifeBuoy className="mr-2  lg:text-2xl text-xl" color="orange"/> },
    { name: "Bots", icon: <LuBot className="lg:mr-2  lg:text-2xl text-xl" color="orange" /> },
    { name: "More", },
  ];

  return (
    <div className="h-full justify-center items-center bg-none w-14 flex flex-col absolute">
      
        {/* <div className="p-4 lg:block hidden">
          <img className=" " src="/logo.png" alt="LOGO" />
        </div> */}

        {/* <div className="p-1 md:block lg:hidden">
          <img className="" src="/logo-sm.png" alt="LOGO" />
        </div> */}
        
        <div className="m-0 lg:m-6 font-bold text-white">
          <ul>
            {menuItems.map((item, index) => (
              <li
                key={index}
                className={`flex cursor-default hover:bg-orange-200 p-3 rounded-lg ${
                  index === isActive ? "bg-orange-200 translate-x-full " : "bg-none"
                }`}
                onClick={() => setisactive(index)}
              >
                <Link to={`/${item.name.toLowerCase()}`} className="flex justify-center items-center" >
                <div className="" > {item.icon} </div>
                {/* <div className="lg:block hidden text-3xl text-gray-500" > {item.name} </div> */}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        
      <div>

      </div>

      {/* <div className="text-white w-full p-5 mx-0 bottom-0 text-center hidden lg:block font-bold text-xl hover:cursor-pointer bg-teal-400">
        <span > <Link to='pricing ' >Pricing </Link> </span>
      </div> */}
    </div>
  );
}

export default SideBar;
