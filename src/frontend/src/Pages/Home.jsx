import React, { useState } from "react";
import SideBar from "../components/SideBar";
import ChatArea from "../components/ChatArea";
import Header from "../components/Header";
import { Navbar } from "flowbite-react";
import { NavLink } from "react-router-dom";
// import Footer from "../components/Footer";

function Home() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="flex flex-col w-full h-[94vh] overflow-hidden bg-gradient-to-tl from-[#B9E0F7]">
      {/* <div className="" >
        <SideBar />
      </div> */}
      <div>
        <Header />
      </div>

      <div className="flex flex-col justify-end h-full z-50 p-10">
        <img
          onClick={toggleSidebar}
          src="/chat_bot.png"
          alt="chat"
          className="right-0 mr-10 w-16 h-16 lg:w-30 lg:h-20 hover:cursor-pointer z-50"
        />

        {/* <ChatArea /> */}

        {isOpen && (
          <div className="inset-1 fixed z-50 lg:w-4/5 lg:h-5/6 mx-auto my-auto lg:mt-32 bg-white shadow-lg rounded-3xl">
            <div className="flex h-full">
              <SideBar />

              <ChatArea />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
