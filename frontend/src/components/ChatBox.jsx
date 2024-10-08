import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

/**
 * The heart and soul of the frotnend. 
 * 
 * 
 * @return {JSX.Element} The rendered ChatBox component
 */
const ChatBox = () => {
  // State variables
  const [messages, setMessages] = useState([]); // Stores chat messages
  const [inputMessage, setInputMessage] = useState(''); // Stores current user input
  const [isLoading, setIsLoading] = useState(false); // Indicates if waiting for a response
  const messagesEndRef = useRef(null); // Reference for auto-scrolling

  /**
   * Scrolls the chat window to the bottom.
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Effect to scroll to bottom when messages change
  useEffect(scrollToBottom, [messages]);

  /**
   * Handles sending a new message.
   * 
   * Regarding the hardcoded IP address - I struggled with CORS issues/ IP resolution
   * for the past three days. I'm not proud of this shortcut, but I had to draw the
   * line somewhere. 
   * 
   * I do intend on bringing this project forward with a few extra features, which I will 
   * discuss at length in the readme, but this part called for special attention, as its
   * a representation of my shame to solve the IP resolution issue T_T.
   * 
   * @param {Event} e - The form submit event
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (inputMessage.trim() !== '') {
      setMessages(prev => [...prev, { text: inputMessage, isUser: true }]);
      setInputMessage('');
      setIsLoading(true);

      try {
        // Send message and get token
        const userMessage = await axios.post('http://172.24.44.8:8000/api/chat',
          { 'message': inputMessage });
        const responseToken = userMessage.data.token;

        // Poll for response
        let response;
        do {
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second between polls
          response = await axios.get(`http://172.24.44.8:8000/api/chat/${responseToken}`);
        } while (response.data.status === 'processing');

        // Add bot response to messages
        setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
      } catch (error) {
        console.error('Error fetching response:', error);
        setMessages(prev => [...prev, { text: "Sorry, there was an error getting the response.", isUser: false }]);
      } finally {
        setIsLoading(false);
      }
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
                <img src="/loading.gif" alt="Loading..." className="h-6 w-6" />
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