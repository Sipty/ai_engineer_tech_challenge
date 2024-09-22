import React from 'react';
import { Rocket } from 'lucide-react';

/**
 * Banner component - The app's flag waves proudly :)  
 * 
 * @return {JSX.Element} The rendered Banner component
 */
const Banner = () => {
  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-4 flex items-center h-16 shadow-lg">
      <Rocket className="w-8 h-8 mr-2 text-white" />
      <h1 className="text-2xl font-extrabold text-white italic transform -skew-x-12">
        Chavdar's Awesome Chatbot
      </h1>
    </div>
  );
};

export default Banner;