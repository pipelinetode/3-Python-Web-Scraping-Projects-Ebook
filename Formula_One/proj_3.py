import pandas as pd
import requests
from typing import List

# Constants
INDEX_URL = "https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix"

def get_grand_prix_list() -> List[str]:
    """Fetches the main list of Grands Prix and cleans the titles for URL construction."""
    try:
        tables = pd.read_html(INDEX_URL)
        # Table index 2 corresponds to the 'Grands Prix' list in the wiki
        gp_df = tables[2]
        
        titles = (
            gp_df['Race title']
            .str.replace(r"\[.*\]", "", regex=True)
            .str.replace(r"\*", "", regex=True)
            .str.strip()
        )
        
        # Convert to Wikipedia URL format (spaces to underscores)
        return [title.replace(" ", "_") for title in titles if title]
    
    except Exception as e:
        print(f"Error fetching the index table: {e}")
        return []

def scrape_individual_gp(gp_slug: str):
    """Fetches tables from a specific Grand Prix Wikipedia page."""
    url = f"https://en.wikipedia.org/wiki/{gp_slug}"
    print(f"Fetching data for: {gp_slug}...")
    
    try:
        # Note: read_html returns a LIST of all tables on the page
        gp_tables = pd.read_html(url)
        
        if gp_tables:
            print(f"Successfully retrieved {len(gp_tables)} tables for {gp_slug}.")
            print(f"First table shape: {gp_tables[0].shape}")
        return gp_tables
        
    except Exception as e:
        print(f"Could not retrieve {url}: {e}")
        return None

def main():
    gp_slugs = get_grand_prix_list()
    
    test_slugs = gp_slugs[:5]
    
    results = {}
    for slug in test_slugs:
        data = scrape_individual_gp(slug)
        if data:
            results[slug] = data

    print("\nScraping complete.")

if __name__ == "__main__":
    main()
