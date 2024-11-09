import React, { useState } from "react";
import axios from "axios";

function CrawlerControl() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleStartCrawl = async () => {
    setLoading(true);
    setMessage("");
    try {
      // Try using the full URL to avoid proxy issues
      const response = await axios.post("http://localhost:5000/start-crawl");

      if (response.data.status === "Crawling completed") {
        setMessage("Crawling completed successfully!");
      } else {
        setMessage("Crawling failed.");
      }
    } catch (error) {
      setMessage("An error occurred while starting the crawl.");
      console.error("Error starting crawl:", error);
      if (error.response) {
        console.error("Error response data:", error.response.data);
        console.error("Error response status:", error.response.status);
      }
    }
    setLoading(false);
  };

  return (
    <div className="crawler-control">
      <h2>Start a New Crawl</h2>
      <button onClick={handleStartCrawl} disabled={loading}>
        {loading ? "Crawling..." : "Start Crawling"}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default CrawlerControl;
