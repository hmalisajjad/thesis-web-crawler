import os
from flask import Flask, jsonify
from flask_cors import CORS
from crawlers.multi_framework_crawler.multi_framework_spider import run_crawler_in_thread
from db.database import load_from_json
import logging
import threading
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Restrict CORS to React frontend origin

logging.basicConfig(level=logging.INFO)

# Global variable to track the crawl status
crawl_in_progress = False


@app.route('/start-crawl', methods=['POST'])
def start_crawl():
    """
    Start the crawling process in a background thread and return an immediate response.
    """
    global crawl_in_progress

    if crawl_in_progress:
        return jsonify({"success": False, "status": "Crawl already in progress"}), 400

    crawl_in_progress = True

    def background_crawl():
        global crawl_in_progress
        try:
            data = run_crawler_in_thread()
            if data:
                logging.info("Crawl completed successfully.")
            else:
                logging.error("Crawl failed or no data found.")
        except Exception as e:
            logging.error(f"Error during crawling: {e}")
        finally:
            crawl_in_progress = False

    thread = threading.Thread(target=background_crawl)
    thread.start()

    return jsonify({"success": True, "status": "Crawl started in background"}), 200


@app.route('/results', methods=['GET'])
def get_results():
    """
    Fetch results from the `chatbot_data.json` file.
    """
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "chatbot_data.json"))
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:  # If data is not empty
                return jsonify({'status': 'Success', 'data': data}), 200
            else:
                return jsonify({'status': 'No data found', 'data': []}), 200
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            return jsonify({'status': 'Error', 'error': 'Invalid JSON format'}), 500
    else:
        return jsonify({'status': 'File not found'}), 404


@app.route('/crawl-status', methods=['GET'])
def crawl_status():
    """
    Check if a crawl is currently in progress.
    """
    global crawl_in_progress
    return jsonify({"in_progress": crawl_in_progress}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
