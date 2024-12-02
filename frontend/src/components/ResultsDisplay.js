import React from "react";

// Add a decodeHTML function to handle decoding of HTML entities.
function decodeHTML(html) {
  const txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

function ResultsDisplay({ results }) {
  console.log(results);

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
                  <a
                    href={item.main_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {item.main_url}
                  </a>
                </td>
                {/* Decode HTML entities in the title */}
                <td>{decodeHTML(item.title)}</td>
                <td>
                  {item.detected_chatbots?.length > 0 ? "Detected" : "None"}
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
