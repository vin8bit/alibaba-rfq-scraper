# ecommerce_books_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
url = "https://books.toscrape.com/catalogue/page-1.html"

# Empty list to store book data
books_data = []

while url:
    print(f"Scraping: {url}")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all book containers
    books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()
        availability = book.find("p", class_="instock availability").text.strip()
        rating = book.p["class"][1]  # Example: 'One', 'Two', 'Three'

        books_data.append({
            "Title": title,
            "Price": price,
            "Availability": availability,
            "Rating": rating
        })

    # Check for next page
    next_page = soup.find("li", class_="next")
    if next_page:
        next_page_url = next_page.a["href"]
        base_url = "https://books.toscrape.com/catalogue/"
        url = base_url + next_page_url
    else:
        url = None  # Stop loop

# Convert to DataFrame
df = pd.DataFrame(books_data)

# Display sample data
print("📚 Scraped Book Data (first 5 rows):")
print(df.head())

# Save data to CSV
df.to_csv("books_data.csv", index=False)
print("\n✅ Data saved to books_data.csv")
