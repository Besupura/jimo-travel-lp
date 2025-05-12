
"""
Scrapes Google Popular Times data and converts it to CSV.
Based on the gmaps_popular_times_scraper library.
"""

import os
import sys
import logging
import pandas as pd
import json
from pathlib import Path
import time
import random
import argparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_popular_times.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/interim")
INPUT_FILE = OUTPUT_DIR / "04_google_enriched_spots.csv"
OUTPUT_FILE = OUTPUT_DIR / "05_popular_times_spots.csv"

MIN_DELAY = 5  # Minimum delay between requests in seconds
MAX_DELAY = 15  # Maximum delay between requests in seconds
MAX_REQUESTS = 100  # Maximum number of requests per run

def setup_webdriver():
    """
    Set up the Chrome webdriver for scraping.
    """
    try:
        logger.info("Setting up Chrome webdriver")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        return driver
    
    except Exception as e:
        logger.error(f"Error setting up webdriver: {e}")
        raise

def load_input_data():
    """
    Load data from the input file.
    """
    try:
        logger.info(f"Loading input data from {INPUT_FILE}")
        
        if not INPUT_FILE.exists():
            logger.error(f"Input file {INPUT_FILE} does not exist")
            return pd.DataFrame()
        
        df = pd.read_csv(INPUT_FILE)
        logger.info(f"Loaded {len(df)} records from {INPUT_FILE}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading input data: {e}")
        raise

def get_google_maps_url(name, address=None, lat=None, lng=None):
    """
    Generate a Google Maps URL for a place.
    """
    base_url = "https://www.google.com/maps/search/"
    
    query = name
    if address:
        query += f" {address}"
    
    if lat is not None and lng is not None:
        query += f"/@{lat},{lng},15z"
    
    query = requests.utils.quote(query)
    
    return f"{base_url}{query}"

def scrape_popular_times(driver, url):
    """
    Scrape popular times data from Google Maps.
    """
    try:
        logger.info(f"Scraping popular times from {url}")
        
        driver.get(url)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-hero-header-title"))
        )
        
        try:
            popular_times_section = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Popular times')]"))
            )
            popular_times_section.click()
            
            time.sleep(2)
        except (TimeoutException, NoSuchElementException):
            logger.warning("Popular times section not found or not clickable")
            return {}
        
        try:
            popular_times_container = driver.find_element(By.CSS_SELECTOR, "div.section-popular-times")
            
            day_elements = popular_times_container.find_elements(By.CSS_SELECTOR, "div.section-popular-times-day")
            
            popular_times_data = {}
            
            for day_element in day_elements:
                day_name = day_element.find_element(By.CSS_SELECTOR, "div.section-popular-times-day-name").text.strip()
                
                hour_bars = day_element.find_elements(By.CSS_SELECTOR, "div.section-popular-times-bar")
                
                hours_data = []
                
                for i, hour_bar in enumerate(hour_bars):
                    hour = 6 + i  # Starting from 6am
                    
                    style = hour_bar.get_attribute("style")
                    height_str = style.split("height: ")[1].split("%;")[0]
                    popularity = int(float(height_str))
                    
                    hours_data.append({
                        "hour": hour,
                        "popularity": popularity
                    })
                
                popular_times_data[day_name] = hours_data
            
            return popular_times_data
        
        except (NoSuchElementException, IndexError) as e:
            logger.warning(f"Error extracting popular times data: {e}")
            return {}
    
    except Exception as e:
        logger.error(f"Error scraping popular times: {e}")
        return {}

def format_popular_times(popular_times_data):
    """
    Format popular times data as a histogram string.
    """
    if not popular_times_data:
        return ""
    
    histogram = []
    
    for day, hours in popular_times_data.items():
        day_data = f"{day}: "
        
        hour_values = []
        for hour_data in hours:
            hour = hour_data["hour"]
            popularity = hour_data["popularity"]
            hour_values.append(f"{hour}:{popularity}")
        
        day_data += ",".join(hour_values)
        histogram.append(day_data)
    
    return "; ".join(histogram)

def scrape_data(df, limit=None):
    """
    Scrape popular times data for each spot in the dataframe.
    """
    try:
        logger.info("Scraping popular times data")
        
        scraped_df = df.copy()
        
        scraped_df['popularity_histogram'] = ''
        
        driver = setup_webdriver()
        
        request_count = 0
        
        for idx, row in scraped_df.iterrows():
            if limit and idx >= limit:
                break
            
            if request_count >= MAX_REQUESTS:
                logger.warning(f"Reached maximum number of requests ({MAX_REQUESTS}). Stopping.")
                break
            
            name = row['name']
            address = row.get('address', '')
            lat = row.get('latitude')
            lng = row.get('longitude')
            
            logger.info(f"Processing spot {idx+1}/{len(scraped_df)}: {name}")
            
            url = get_google_maps_url(name, address, lat, lng)
            
            popular_times_data = scrape_popular_times(driver, url)
            
            request_count += 1
            
            popularity_histogram = format_popular_times(popular_times_data)
            
            scraped_df.at[idx, 'popularity_histogram'] = popularity_histogram
            
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            logger.info(f"Waiting {delay:.2f} seconds before next request")
            time.sleep(delay)
            
            if (idx + 1) % 5 == 0:
                logger.info(f"Processed {idx+1} spots, made {request_count} requests")
        
        driver.quit()
        
        logger.info(f"Scraping complete. Made {request_count} requests.")
        
        return scraped_df
    
    except Exception as e:
        logger.error(f"Error scraping data: {e}")
        raise

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Scrape Google Popular Times data')
    parser.add_argument('--limit', type=int, help='Limit the number of spots to process')
    return parser.parse_args()

def main():
    """
    Main function to scrape popular times data.
    """
    try:
        args = parse_args()
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        df = load_input_data()
        
        if len(df) == 0:
            logger.error("No input data available")
            return pd.DataFrame()
        
        scraped_df = scrape_data(df, limit=args.limit)
        
        scraped_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(scraped_df)} spots with popular times data to {OUTPUT_FILE}")
        
        return scraped_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
