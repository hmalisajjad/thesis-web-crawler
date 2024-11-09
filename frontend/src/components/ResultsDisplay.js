// frontend/src/components/ResultsDisplay.js

import React, { useState, useEffect } from "react";
import axios from "axios";

function ResultsDisplay() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const fetchResults = async () => {
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.get("http://localhost:5000/results");
      console.log(response.data.data);

      setResults(response.data.data);
    } catch (error) {
      setMessage("No results found or an error occurred.");
      console.error("Error fetching results:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    // Fetch results initially and set up polling every 30 seconds
    fetchResults();
    const interval = setInterval(() => {
      fetchResults();
    }, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="results-display">
      <h2>Crawl Results</h2>
      {loading && <p>Loading results...</p>}
      {message && <p>{message}</p>}
      {!loading && results.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Title</th>
              <th>Chatbots Detected</th>
              <th>Keywords Detected</th>
              <th>Date Collected</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item, index) => (
              <tr key={index}>
                <td>
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    {item.url}
                  </a>
                </td>
                <td>{item.title}</td>
                <td>
                  {item.detected_chatbots.length > 0 ? (
                    <ul>
                      {item.detected_chatbots.map((chatbot, idx) => (
                        <li key={idx}>
                          <a
                            href={chatbot}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Chatbot {idx + 1}
                          </a>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    "None"
                  )}
                </td>
                <td>{item.keywords_detected.join(", ") || "None"}</td>
                <td>{item.date_collected}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ResultsDisplay;
