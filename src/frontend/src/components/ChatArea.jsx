import React, { useRef, useState, useEffect } from "react";
import { GrSend } from "react-icons/gr";
import { useWebSocket } from "../services/useWebSocket"; // Adjust path
import { v4 as uuidv4 } from "uuid";
import { GrAttachment } from "react-icons/gr";

function ChatArea() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [easterEgg, setEasterEgg] = useState(false);
  
  const { response, isOpen, isBotResponseComplete, sendMessage } = useWebSocket(
    "ws://localhost:8000/ws",
    setEasterEgg
  );

  // Add user message
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() === "") return;

    const userMessage = { id: uuidv4(), user: "User", message: input };
    setMessages((prev) => [...prev, userMessage]);

    sendMessage(input); // Send to WebSocket
    setInput("");
    if (textareaRef.current) textareaRef.current.focus();
  };

  // Detect "Enter"
  const handlekeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Listen to bot response
  useEffect(() => {
    if (response !== "") {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        // Append to previous bot message if last was bot and still typing
        if (last && last.user === "Bot" && !isBotResponseComplete) {
          return [
            ...prev.slice(0, -1),
            { ...last, message: last.message + response },
          ];
        }
        return [...prev, { id: uuidv4(), user: "Bot", message: response }];
      });
    }
  }, [response]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="h-full w-[100vw] flex flex-col items-center justify-between mx-auto bg-gradient-to-tl from-[#F4EDCD]">
      <div className="flex flex-col lg:w-[80vw] max-w-screen mb-0 overflow-y-auto lg:p-4 hide-scrollbar">
        {messages.map((m, index) => (
          <div
            key={m.id || index}
            className={`mb-2 flex ${
              m.user === "User" ? "justify-end ml-10" : "justify-start mr-10"
            }`}
          >
            <div
              className={`p-2 m-2 rounded-xl ${
                m.user === "User"
                  ? "bg-sky-200 rounded-tr-none drop-shadow-lg shadow-gray-400 p-4 text-xl"
                  : "text-xl  rounded-tl-none bg-orange-100 drop-shadow-lg shadow-gray-400 p-4"
              }`}
            >
              {/* <strong>{m.user}: </strong> */}
              {m.message}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="w-full p-4 shadow-md">
        <form
          className="flex items-center justify-center gap-5"
          onSubmit={handleSubmit}
        >
          <label>
            <input type="file" className="hidden" />
            <GrAttachment size={25} />
          </label>

          <textarea
            value={input}
            ref={textareaRef}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => {
              setTimeout(() => {
                textareaRef.current?.scrollIntoView({
                  behavior: "smooth",
                  block: "center",
                });
              }, 100);
            }}
            className=" rounded-xl p-3 w-3/5 resize-none h-12 lg:h-24 focus:outline-none focus:border-none "
            placeholder="Enter your query..."
            onKeyDown={handlekeydown}
          />
          <button type="submit">
            <GrSend size={30} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatArea;
