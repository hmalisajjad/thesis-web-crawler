import os
from flask import Flask, jsonify
from flask_cors import CORS
from crawlers.multi_framework_crawler.multi_framework_spider import run_crawler_in_thread
import logging
import threading
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Restrict CORS to React frontend origin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

crawl_in_progress = False


@app.route('/start-crawl', methods=['POST'])
def start_crawl():
    """
    API to start the crawling process.
    """
    global crawl_in_progress

    if crawl_in_progress:
        logger.warning("Crawl already in progress.")
        return jsonify({"success": False, "status": "Crawl already in progress"}), 400

    crawl_in_progress = True

    def background_crawl():
        """
        Run the crawler in a separate thread and update the status.
        """
        global crawl_in_progress
        try:
            data = run_crawler_in_thread()
            if data:
                logger.info("Crawl completed successfully.")
            else:
                logger.error("Crawl failed or no data found.")
        except Exception as e:
            logger.exception(f"Error during crawling: {e}")
        finally:
            crawl_in_progress = False

    thread = threading.Thread(target=background_crawl)
    thread.daemon = True  # Ensure thread exits with the main program
    thread.start()

    logger.info("Crawl started in the background.")
    return jsonify({"success": True, "status": "Crawl started in background"}), 200


@app.route('/results', methods=['GET'])
def get_results():
    """
    API to fetch crawl results.
    """
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "chatbot_data.json"))
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                logger.info(f"Returning {len(data)} results.")
                return jsonify({'status': 'Success', 'data': data}), 200
            else:
                logger.info("No crawl data found.")
                return jsonify({'status': 'No data found', 'data': []}), 200
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
            return jsonify({'status': 'Error', 'error': 'Invalid JSON format'}), 500
    else:
        logger.warning("Results file not found.")
        return jsonify({'status': 'File not found'}), 404


@app.route('/crawl-status', methods=['GET'])
def crawl_status():
    """
    API to check the status of the crawling process.
    """
    global crawl_in_progress
    logger.info(f"Crawl status requested: {'In Progress' if crawl_in_progress else 'Not In Progress'}")
    return jsonify({"in_progress": crawl_in_progress}), 200


if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.exception(f"Application encountered an error: {e}")
