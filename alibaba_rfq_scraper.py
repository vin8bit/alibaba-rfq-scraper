import logging
import random
import csv
from datetime import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from typing import Optional, List, Dict
import time

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

class RateLimiter:
    def __init__(self, max_per_second: float):
        self.max_per_second = max_per_second
        self.last_request_time = 0

    def wait(self):
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        time_to_wait = 1.0 / self.max_per_second - time_passed

        if time_to_wait > 0:
            time.sleep(time_to_wait)

        self.last_request_time = time.time()

def check_proxy(proxy: str) -> bool:
    """Check if proxy is working."""
    try:
        response = requests.get('https://www.alibaba.com', 
                              proxies={'http': proxy, 'https': proxy},
                              timeout=10)
        return response.status_code == 200
    except RequestException:
        return False

def scrape_rfq_listings(
    url="https://sourcing.alibaba.com/rfq/rfq_search_list.htm?spm=a2700.8073608.1998677541.1.82be65aaoUUItC&&country=AE&&recently=Y&&tracelog=newest",
    output_csv='alibaba_rfq_listings.csv',
    wait_time=10,
    max_retries=3,
    proxy: Optional[str] = None,
    requests_per_second: float = 1.0
):
    """
    Scrape Alibaba RFQ listings and save to CSV.
    """
    # Initialize rate limiter
    rate_limiter = RateLimiter(requests_per_second)
    
    # Validate proxy if provided
    if proxy:
        if not check_proxy(proxy):
            logging.error("Provided proxy is not working. Proceeding without proxy.")
            proxy = None
        else:
            logging.info("Using proxy: %s", proxy)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")
    logging.info(f"Using User-Agent: {user_agent}")

    driver = None
    for attempt in range(1, max_retries + 1):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(url)
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'alife-bc-brh-rfq-list__row'))
            )
            logging.info(f"Page loaded successfully on attempt {attempt}")
            break
        except (TimeoutException, WebDriverException) as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
            if driver:
                driver.quit()
            if attempt == max_retries:
                logging.error("Max retries reached. Exiting.")
                return
            sleep(3)

    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rfq_rows = soup.find_all('div', class_='next-row next-row-no-padding alife-bc-brh-rfq-list__row')
        logging.info(f"Found {len(rfq_rows)} RFQ entries")
        driver.quit()
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        if driver:
            driver.quit()
        return

    data = []
    scraping_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for idx, row in enumerate(rfq_rows, 1):
        try:
            # Apply rate limiting
            rate_limiter.wait()
            
            rfq_link = row.find('a', class_='brh-rfq-item__subject-link')['href']
            rfq_id = rfq_link.split('uuid=')[1].split('&')[0] if 'uuid=' in rfq_link else 'N/A'
            title_elem = row.find('a', class_='brh-rfq-item__subject-link')
            title = title_elem['title'] if title_elem else 'N/A'
            buyer_info = row.find('div', class_='avatar')
            buyer_name = buyer_info.find('div', class_='text').get_text(strip=True) if buyer_info else 'N/A'
            buyer_image = buyer_info.find('img')['src'] if buyer_info and buyer_info.find('img') else 'N/A'
            inquiry_time = row.find('div', class_='brh-rfq-item__publishtime').get_text(strip=True).replace('Date Posted:', '') if row.find('div', class_='brh-rfq-item__publishtime') else 'N/A'
            quotes_left = row.find('div', class_='brh-rfq-item__quote-left').get_text(strip=True).replace('Quotes Left', '').strip() if row.find('div', class_='brh-rfq-item__quote-left') else 'N/A'
            country = row.find('img', class_='brh-rfq-item__country-flag')['title'] if row.find('img', class_='brh-rfq-item__country-flag') else 'N/A'
            quantity = row.find('span', class_='brh-rfq-item__quantity-num').get_text(strip=True) if row.find('span', class_='brh-rfq-item__quantity-num') else 'N/A'
            tags = [tag.get_text(strip=True) for tag in row.find_all('div', class_='next-tag-body')]
            email_confirmed = 'Yes' if 'Email Confirmed' in tags else 'No'
            experienced_buyer = 'Yes' if 'Experienced Buyer' in tags else 'No'
            complete_order_via_rfq = 'Yes' if 'Complete Order via RFQ' in tags else 'No'
            typical_replies = 'Yes' if 'Typical Replies' in tags else 'No'
            interactive_user = 'Yes' if 'Interactive User' in tags else 'No'

            data.append([
                rfq_id, title, buyer_name, buyer_image, inquiry_time,
                quotes_left, country, quantity, email_confirmed,
                experienced_buyer, complete_order_via_rfq, typical_replies,
                interactive_user, rfq_link, datetime.now().strftime('%Y-%m-%d'), scraping_date
            ])
        except Exception as e:
            logging.warning(f"Row {idx} error: {e}")
            continue

    headers = [
        'RFQ ID.', 'Title', 'Buyer Name', 'Buyer Image', 'Inquiry Time',
        'Quotes Left', 'Country', 'Quantity Required', 'Email Confirmed',
        'Experienced Buyer', 'Complete Order via RFQ', 'Typical Replies',
        'Interactive User', 'Inquiry URL', 'Inquiry Date', 'Scraping Date'
    ]

    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        logging.info(f"Saved {len(data)} entries to {output_csv}")
    except Exception as e:
        logging.error(f"CSV saving error: {e}")

if __name__ == "__main__":
    # Example usage with all new features
    scrape_rfq_listings(
        wait_time=15,  # Increased wait time for better reliability
        max_retries=5,  # Increased retries
        proxy=None,  # Add your proxy here if needed e.g., "http://your-proxy:8080"
        requests_per_second=0.5  # Conservative rate limiting
    )

