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

 
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() === "") return;

    const userMessage = { id: uuidv4(), user: "User", message: input };
    setMessages((prev) => [...prev, userMessage]);

    sendMessage(input); 
    setInput("");
    if (textareaRef.current) textareaRef.current.focus();
  };


  const handlekeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (response !== "") {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
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
    <div className="h-full w-full flex flex-col bg-gradient-to-tl from-[#F4EDCD] border-2 border-gray-200 rounded-lg">
    {/* Messages area */}
    <div className="flex-1 overflow-y-auto hide-scrollbar w-3/5 mx-auto p-4">
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
                ? "bg-sky-200 rounded-tr-none drop-shadow-lg shadow-gray-400 lg:p-4 text-sm lg:text-l"
                : "rounded-tl-none bg-orange-100 drop-shadow-lg shadow-gray-400 lg:p-4 text-sm lg:text-l"
            }`}
          >
           <span className="font-bold" >{m.user === "User" ? "You: " : "Bot: "}</span> 
            {m.message}
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>

    {/* Input area */}
    <div className="w-full p-2 shadow-md border-t">
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
          className="rounded-xl p-1 lg:p-3 w-3/5 resize-none h-12 lg:h-20 focus:outline-none text-sm lg:text-lg"
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
