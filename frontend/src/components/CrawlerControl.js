// frontend/src/components/CrawlerControl.js

import React from "react";

function CrawlerControl({ onStartCrawl, loading, message }) {
  return (
    <div className="crawler-control">
      <h2>Start a New Crawl</h2>
      <button onClick={onStartCrawl} disabled={loading}>
        {loading ? "Crawling..." : "Start Crawling"}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default CrawlerControl;
