import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Constants
BASE_URL = "https://www.zillow.com/orlando-fl/apartments/{page}_p/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/92.0.4515.159 Safari/537.36"
}

def fetch_page_html(page_num: int) -> str:
    """Fetches the HTML content for a specific page number."""
    url = BASE_URL.format(page=page_num)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.text

def parse_apartment_data(html: str) -> list[dict]:
    """Parses apartment details from Zillow HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    
    cards = soup.find_all("div", {"class": "StyledPropertyCardDataWrapper-c11n-8-73-8__sc-1omp4c3-0 gXNuqr property-card-data"})
    
    extracted_data = []
    
    for card in cards:
        item = {
            "price": None,
            "address": None,
            "space": None
        }
        
        # Helper to safely extract text
        price_tag = card.find("div", {"class": "StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0 hRqIYX"})
        addr_tag = card.find("a", {"class": "StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0 lhIXlm property-card-link"})
        space_tag = card.find("div", {"class": "StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0 ghGYOB"})

        if price_tag: item["price"] = price_tag.get_text(strip=True)
        if addr_tag: item["address"] = addr_tag.get_text(strip=True)
        if space_tag: item["space"] = space_tag.get_text(strip=True)
        
        extracted_data.append(item)
        
    return extracted_data

def scrape_zillow(start_page: int, end_page: int) -> pd.DataFrame:
    """Orchestrates the scraping of multiple pages."""
    all_records = []
    
    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")
        try:
            html = fetch_page_html(page)
            page_data = parse_apartment_data(html)
            all_records.extend(page_data)
            
            # Pause to avoid bot detection
            time.sleep(1) 
        except Exception as e:
            print(f"Failed to scrape page {page}: {e}")
            
    return pd.DataFrame(all_records)

def main():
    # Scrape pages 1 through 10
    apartment_df = scrape_zillow(1, 10)
    
    if not apartment_df.empty:
        print(f"Successfully scraped {len(apartment_df)} listings.")
        print(apartment_df.head())
        # apartment_df.to_csv("orlando_apartments.csv", index=False)
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
