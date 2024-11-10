// frontend/src/App.js

import React, { useState } from "react";
import CrawlerControl from "./components/CrawlerControl";
import ResultsDisplay from "./components/ResultsDisplay";
import axios from "axios";
import "./App.css";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleStartCrawl = async () => {
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.post("http://localhost:5000/start-crawl");

      if (response.data.status === "Crawling completed") {
        setMessage("Crawling completed successfully!");
        fetchResults(); // Fetch updated results after crawling
      } else {
        setMessage("Crawling failed.");
      }
    } catch (error) {
      setMessage("An error occurred while starting the crawl.");
      console.error("Error starting crawl:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get("http://localhost:5000/results");
      setResults(response.data.data);
    } catch (error) {
      setMessage("Failed to fetch results.");
      console.error("Error fetching results:", error);
    }
  };

  return (
    <div className="App">
      <h1>Chatbot Detection Web Crawler</h1>
      <CrawlerControl
        onStartCrawl={handleStartCrawl}
        loading={loading}
        message={message}
      />
      <ResultsDisplay results={results} />
    </div>
  );
}

export default App;
