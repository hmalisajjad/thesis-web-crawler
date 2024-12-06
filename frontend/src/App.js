import React, { useEffect, useState } from "react";
import CrawlerControl from "./components/CrawlerControl";
import ResultsDisplay from "./components/ResultsDisplay";
import axios from "axios";
import "./App.css";

function decodeHTML(html) {
  const txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [crawlInProgress, setCrawlInProgress] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      checkCrawlStatus();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const checkCrawlStatus = async () => {
    try {
      const response = await axios.get("http://localhost:5000/crawl-status");
      setCrawlInProgress(response.data.in_progress);
      if (!response.data.in_progress) {
        fetchResults();
      }
    } catch (error) {
      console.error("Error checking crawl status:", error);
    }
  };

  const handleStartCrawl = async () => {
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.post(
        "http://localhost:5000/start-crawl",
        { dataset_size: 100 },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (response.data.success) {
        setMessage("Crawling started successfully!");
      } else {
        setMessage(response.data.status);
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
      if (response.data.status === "Success" && response.data.data.length > 0) {
        const decodedResults = response.data.data.map((result) => ({
          ...result,
          title: decodeHTML(result.title),
        }));
        setResults(decodedResults);
        setMessage("");
      } else if (response.data.status === "No data found") {
        setMessage("No crawl results available yet.");
        setResults([]);
      } else {
        setMessage("Failed to fetch results.");
      }
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
        loading={loading || crawlInProgress}
        message={message}
      />
      <ResultsDisplay results={results} />
    </div>
  );
}

export default App;
