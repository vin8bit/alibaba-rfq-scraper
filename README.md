📂 Project Structure

alibaba_rfq_scraper.py → Main Python script for scraping RFQ listings.

alibaba_rfq_listings.csv → Output file containing scraped RFQ data.

web_screenshot.PNG → Example screenshot of the scraped webpage.

vineet_web_scraping/ → Project folder with additional scripts/resources.

🚀 Features

Scrapes Alibaba RFQ listings automatically.

Extracts product details, categories, and supplier information.

Saves data into CSV format for further use.

Captures webpage screenshots for documentation and debugging.

Easy to extend for other e-commerce platforms.

🔧 Requirements

Python 3.x

requests

beautifulsoup4

pandas

selenium (if used for dynamic scraping)


Usage:
Clone the repository and install dependencies using pip install -r requirements.txt.
Run alibaba_rfq_scraper.py to start scraping RFQ listings.
Scraped data will be saved in alibaba_rfq_listings.csv.
Make sure to configure any required browser drivers if using Selenium.
Use the web_screenshot.PNG to verify page layout consistency.
