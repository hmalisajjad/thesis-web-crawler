// frontend/src/components/ResultsDisplay.js

import React from "react";

function ResultsDisplay({ results }) {
  return (
    <div className="results-display">
      <h2>Crawl Results</h2>
      {results.length === 0 ? (
        <p>No results found.</p>
      ) : (
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
                        <li key={idx}>Chatbot {idx + 1}</li>
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
