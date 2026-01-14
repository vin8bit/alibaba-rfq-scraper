# 🛒 Alibaba RFQ Web Scraper

A Python-based web scraping project that automatically extracts **RFQ (Request for Quotation)** listings from Alibaba and stores them in a structured CSV format. The project is designed to be simple, extensible, and useful for data analysis or lead generation.

---

## 📂 Project Structure

├── alibaba_rfq_scraper.py # Main Python script for scraping RFQ listings
├── alibaba_rfq_listings.csv # Output file containing scraped RFQ data
├── web_screenshot.PNG # Example screenshot of the scraped webpage
├── vineet_web_scraping/ # Additional scripts and resources
└── requirements.txt # Python dependencies

---

## 🚀 Features

- Automatically scrapes Alibaba RFQ listings
- Extracts:
  - Product details
  - Categories
  - Supplier information
- Saves scraped data in **CSV format** for further processing

---

## 🔧 Requirements

- Python **3.x**
- `beautifulsoup4`
- `pandas`
- `selenium`

---

## ⚙️ Installation
```
pip install -r requirements.txt
```

## ▶️ Run the scraper:
```
python alibaba_rfq_scraper.py
```
### The scraped RFQ data will be saved to:
```
alibaba_rfq_listings.csv
```
