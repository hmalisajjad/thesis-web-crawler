#**Web Crawler for Chatbot Detection**
Chatbots are becoming increasingly popular on websites as they offer automated customer support. However, there is a lack of comprehensive datasets that document the various chatbot implementations across different websites. Existing datasets are often limited to specific types of chatbots or interactions, making them less useful for general research. This thesis aims to fill this gap by developing a web crawler capable of discovering and gathering different chatbots in websites. The objective is to create a dataset covering a wide range of chatbot implementations ‘in the wild’, as a basis for further research

##**Prerequisites**
Before running the project, ensure you have the following installed:

Python 3.12+
Scrapy
Flask
BeautifulSoap
Selenium
Node.js and npm
Google Chrome
ChromeDriver
Download ChromeDriver and Update the ChromeDriver path in multi_framework_spider.py under the Service initialization:
###**chrome_service = Service("C:\\WebDrivers\\chromedriver-win64\\chromedriver.exe")**

#**Important Notes**
Please make sure ChromeDriver is installed and the path is correctly configured in multi_framework_spider.py.
So that you will achieve successful dynamic crawling, 
###**update the ChromeDriver location:**
chrome_service = Service("C:\\Path\\To\\chromedriver.exe")

##**Installation**

###**Backend Setup**
Clone the repository:(
    git clone <repository_url>
    cd thesis-web-crawler
)

Navigate to the Backend directory:
cd backend

###**Set up a virtual environment:**
python -m venv venv

###**Activate the virtual environment:**
venv\Scripts\activate

###**Install the required Python packages:**
pip install -r requirements.txt

###**Frontend Setup**
Navigate to the frontend directory:
cd frontend

###**Install dependencies:**
npm install

##**How to Run Crawler**

###**For Backend**
Navigate to the Backend directory:
cd backend

###**Activate the virtual environment:**
venv\Scripts\activate

###**Start the Flask server:**
python app.py
The backend will run on http://localhost:5000.

###**For Frontend**
Navigate to the frontend directory:
cd frontend

###**Start the React application:**
npm start
The frontend will run on http://localhost:3000.

##**Testing**

###**Set up a virtual environment:**
python -m venv venv

##**Activate the virtual environment:**
venv\Scripts\activate

Navigate to the test directory:
cd tests

##**Run the tests using pytest:**

###**For Accuracy**
pytest test_accuracy.py

###**For Scalability**
pytest test_scalability.py

###**For Flexibility**
pytest test_flexibility.py

###**For Metadata**
pytest test_metadata.py

###**For Efficiency**
pytest test_efficiency.py

###**For Robustness**
pytest test_robustness.py

###**For Ethical_compliance**
pytest test_ethical_compliance.py

###**For API**
pytest test_api.py