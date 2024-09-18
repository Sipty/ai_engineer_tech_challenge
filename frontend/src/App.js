import React from 'react';
import './App.css';
import ChatBox from './components/ChatBox';
import Banner from './components/Banner';

function App() {
  return (
    <div className="App flex flex-col h-screen bg-black">
      <Banner />
      <div className="flex-grow">
        <ChatBox />
      </div>
    </div>
  );
}

export default App;