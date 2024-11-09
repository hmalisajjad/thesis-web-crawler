// frontend/src/App.js

import React from "react";
import CrawlerControl from "./components/CrawlerControl";
import ResultsDisplay from "./components/ResultsDisplay";
import "./App.css"; // Optional: Add CSS for styling

function App() {
  return (
    <div className="App">
      <h1>Chatbot Detection Web Crawler</h1>
      <CrawlerControl />
      <ResultsDisplay />
    </div>
  );
}

export default App;
