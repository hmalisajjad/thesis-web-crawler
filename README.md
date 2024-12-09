#**Web Crawler for Chatbot Detection**<br>
Chatbots are becoming increasingly popular on websites as they offer automated customer support. However, there is a lack of comprehensive datasets that document the various chatbot implementations across different websites. Existing datasets are often limited to specific types of chatbots or interactions, making them less useful for general research. This thesis aims to fill this gap by developing a web crawler capable of discovering and gathering different chatbots in websites. The objective is to create a dataset covering a wide range of chatbot implementations ‘in the wild’, as a basis for further research

##**Prerequisites**<br>
Before running the project, ensure you have the following installed:<br>

Python 3.12+<br>
Scrapy<br>
Flask<br>
BeautifulSoap<br>
Selenium<br>
Node.js and npm<br>
Google Chrome<br>
ChromeDriver<br>
Download ChromeDriver and Update the ChromeDriver path in multi_framework_spider.py under the Service initialization:<br>
###**chrome_service = Service("C:\\WebDrivers\\chromedriver-win64\\chromedriver.exe")**<br>

#**Important Notes**<br>
Please make sure ChromeDriver is installed and the path is correctly configured in multi_framework_spider.py.<br>
So that you will achieve successful dynamic crawling, <br>
###**update the ChromeDriver location:**<br>
chrome_service = Service("C:\\Path\\To\\chromedriver.exe")<br>

##**Installation**<br>

###**Backend Setup**<br>
Clone the repository:(<br>
    git clone <repository_url><br>
    cd thesis-web-crawler<br>
)<br>

Navigate to the Backend directory:<br>
cd backend<br>

###**Set up a virtual environment:**<br>
python -m venv venv<br>

###**Activate the virtual environment:**<br>
venv\Scripts\activate<br>

###**Install the required Python packages:**<br>
pip install -r requirements.txt<br>

###**Frontend Setup**<br>
Navigate to the frontend directory:<br>
cd frontend<br>

###**Install dependencies:**<br>
npm install<br>

##**How to Run Crawler**<br>

###**For Backend**<br>
Navigate to the Backend directory:<br>
cd backend<br>

###**Activate the virtual environment:**<br>
venv\Scripts\activate<br>

###**Start the Flask server:**<br>
python app.py<br>
The backend will run on http://localhost:5000.<br>

###**For Frontend**<br>
Navigate to the frontend directory:<br>
cd frontend<br>

###**Start the React application:**<br>
npm start<br>
The frontend will run on http://localhost:3000.<br>

##**Testing**<br>

###**Set up a virtual environment:**<br>
python -m venv venv<br>

##**Activate the virtual environment:**<br>
venv\Scripts\activate<br>

Navigate to the test directory:<br>
cd tests<br>

##**Run the tests using pytest:**<br>

###**For Accuracy**<br>
pytest test_accuracy.py<br>

###**For Scalability**<br>
pytest test_scalability.py<br>

###**For Flexibility**<br>
pytest test_flexibility.py<br>

###**For Metadata**<br>
pytest test_metadata.py<br>

###**For Efficiency**<br>
pytest test_efficiency.py<br>

###**For Robustness**<br>
pytest test_robustness.py<br>

###**For Ethical_compliance**<br>
pytest test_ethical_compliance.py<br>

###**For API**<br>
pytest test_api.py<br>