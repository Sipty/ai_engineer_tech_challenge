import React, { useState, useRef, useEffect } from 'react';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim() !== '') {
      setMessages([...messages, { text: inputMessage, isUser: true }]);
      setInputMessage('');
      setIsLoading(true);
      // Simulate a response (TODO: replace with API call)
      setTimeout(() => {
        setMessages(prev => [...prev, { text: "This is a simulated response.", isUser: false }]);
        setIsLoading(false);
      }, 1500);
    }
  };

  return (
    <div className="flex justify-center items-center h-[calc(100vh-4rem)] bg-black p-4">
      <div className="w-full max-w-4xl h-full flex flex-col bg-gray-900 rounded-lg overflow-hidden shadow-lg">
        <div className="flex-1 overflow-y-auto px-6 py-4 bg-gray-800">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}>
              <div className={`rounded-lg px-4 py-2 max-w-[80%] ${
                message.isUser
                  ? 'bg-gray-700 text-white'
                  : 'bg-blue-900 text-white'
              }`}>
                {message.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-700 rounded-lg p-2">
                <img src="loading.gif" alt="Loading..." className="w-6 h-6" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="px-4 py-3 bg-gray-900">
          <form onSubmit={handleSendMessage} className="flex">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="flex-1 bg-gray-800 text-white rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              placeholder="Type a message..."
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-6 py-2 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base font-medium"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;