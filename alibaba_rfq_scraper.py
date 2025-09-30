from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

def scrape_rfq_listings():
    try:
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        # Load the page
        url = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?spm=a2700.8073608.1998677541.1.82be65aaoUUItC&&country=AE&&recently=Y&&tracelog=newest"
        driver.get(url)
        time.sleep(5)  # Wait for dynamic content

        # Parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        # Find RFQ rows
        rfq_rows = soup.find_all('div', class_='next-row next-row-no-padding alife-bc-brh-rfq-list__row')
        print(f"Found {len(rfq_rows)} RFQ entries")

        # Prepare data list
        data = []
        scraping_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for row in rfq_rows:
            try:
                # Extract RFQ ID
                rfq_link = row.find('a', class_='brh-rfq-item__subject-link')['href']
                rfq_id = rfq_link.split('uuid=')[1].split('&')[0] if 'uuid=' in rfq_link else 'N/A'

                # Extract title
                title_elem = row.find('a', class_='brh-rfq-item__subject-link')
                title = title_elem['title'] if title_elem else 'N/A'

                # Extract buyer info
                buyer_info = row.find('div', class_='avatar')
                buyer_name = buyer_info.find('div', class_='text').get_text(strip=True) if buyer_info else 'N/A'
                buyer_image = buyer_info.find('img')['src'] if buyer_info and buyer_info.find('img') else 'N/A'

                # Extract other details
                inquiry_time = row.find('div', class_='brh-rfq-item__publishtime').get_text(strip=True).replace('Date Posted:', '') if row.find('div', class_='brh-rfq-item__publishtime') else 'N/A'
                quotes_left = row.find('div', class_='brh-rfq-item__quote-left').get_text(strip=True).replace('Quotes Left', '').strip() if row.find('div', class_='brh-rfq-item__quote-left') else 'N/A'
                country = row.find('img', class_='brh-rfq-item__country-flag')['title'] if row.find('img', class_='brh-rfq-item__country-flag') else 'N/A'
                quantity = row.find('span', class_='brh-rfq-item__quantity-num').get_text(strip=True) if row.find('span', class_='brh-rfq-item__quantity-num') else 'N/A'

                # Check for buyer tags
                tags = [tag.get_text(strip=True) for tag in row.find_all('div', class_='next-tag-body')]
                email_confirmed = 'Yes' if 'Email Confirmed' in tags else 'No'
                experienced_buyer = 'Yes' if 'Experienced Buyer' in tags else 'No'
                complete_order_via_rfq = 'Yes' if 'Complete Order via RFQ' in tags else 'No'
                typical_replies = 'Yes' if 'Typical Replies' in tags else 'No'
                interactive_user = 'Yes' if 'Interactive User' in tags else 'No'

                # Append data
                data.append([
                    rfq_id,
                    title,
                    buyer_name,
                    buyer_image,
                    inquiry_time,
                    quotes_left,
                    country,
                    quantity,
                    email_confirmed,
                    experienced_buyer,
                    complete_order_via_rfq,
                    typical_replies,
                    interactive_user,
                    rfq_link,
                    datetime.now().strftime('%Y-%m-%d'),
                    scraping_date
                ])
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

        # Save to CSV
        headers = [
            'RFQ ID', 'Title', 'Buyer Name', 'Buyer Image', 'Inquiry Time',
            'Quotes Left', 'Country', 'Quantity Required', 'Email Confirmed',
            'Experienced Buyer', 'Complete Order via RFQ', 'Typical Replies',
            'Interactive User', 'Inquiry URL', 'Inquiry Date', 'Scraping Date'
        ]
        
        with open('alibaba_rfq_listings.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        
        print(f"Successfully saved {len(data)} entries to alibaba_rfq_listings.csv")

    except Exception as e:
        print(f"Critical error: {str(e)}")

if __name__ == "__main__":
    scrape_rfq_listings()