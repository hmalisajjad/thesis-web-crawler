import os
from flask import Flask, jsonify
from flask_cors import CORS
from crawlers.multi_framework_crawler.multi_framework_spider import run_crawler
from db.database import load_from_json
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.INFO)

@app.route('/start-crawl', methods=['POST'])
def start_crawl():
    try:
        logging.info("Received request to start crawling.")
        result = run_crawler()
        if result:
            logging.info("Crawling completed successfully.")
            return jsonify({"success": True, 'status': 'Crawling completed', 'data': result}), 200
        else:
            logging.error("Crawling failed or no data found.")
            return jsonify({"success": False, 'status': 'Crawling failed'}), 500
    except Exception as e:
        app.logger.error(f"Crawling error: {e}")
        return jsonify({'status': 'Crawling encountered an error', 'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    data = load_from_json('chatbot_data.json')  # Load from backend directory
    if data:
        return jsonify({'status': 'Success', 'data': data}), 200
    elif os.path.exists('chatbot_data.json'):
        # File exists but is empty or invalid
        return jsonify({'status': 'No data found'}), 404
    else:
        # File does not exist
        return jsonify({'status': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
