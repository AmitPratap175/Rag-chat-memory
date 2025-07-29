import React from "react";
import SideBar from "../components/SideBar";
import ChatArea from "../components/ChatArea";
import Header from "../components/Header";
// import Footer from "../components/Footer";

function Home() {
  return (
    <div className="flex w-full h-[98vh] overflow-hidden">
      <div className="" >
        <SideBar />
      </div>
      <div className="w-full flex flex-col h-full mx-auto items-center justify-between">
        
        <Header />
        <ChatArea />
      </div>
    </div>
  );
}

export default Home;
