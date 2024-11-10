# app.py
import os
import asyncio

# Set SelectorEventLoop on Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from flask import Flask, jsonify, request
from flask_cors import CORS
from crawlers.multi_framework_crawler.multi_framework_spider import run_crawler, run_crawler_in_thread  # Import your function here
from db.database import save_to_json, load_from_json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/start-crawl', methods=['POST'])
def start_crawl():
    try:
        result = run_crawler_in_thread()
        if result:
            # save_to_json(result, 'chatbot_data.json')  # Save to backend directory
            return jsonify({'status': 'Crawling completed', 'data': result}), 200
        else:
            return jsonify({'status': 'Crawling failed'}), 500
    except Exception as e:
        app.logger.error(f"Crawling error: {e}")
        return jsonify({'status': 'Crawling encountered an error', 'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    data = load_from_json('chatbot_data.json')  # Load from backend directory
    if data:
        return jsonify({'status': 'Success', 'data': data}), 200
    else:
        return jsonify({'status': 'No data found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
