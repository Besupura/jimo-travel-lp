
"""
Uses the Google Places API to enrich the data with additional information
such as address, opening hours, and summary.
"""

import os
import sys
import logging
import pandas as pd
import requests
import json
from pathlib import Path
import time
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_google.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place"
OUTPUT_DIR = Path("data/interim")
INPUT_FILES = [
    OUTPUT_DIR / "01_nln_spots.csv",
    OUTPUT_DIR / "02_ok_od_spots.csv",
    OUTPUT_DIR / "03_osm_spots.csv"
]
OUTPUT_FILE = OUTPUT_DIR / "04_google_enriched_spots.csv"

REQUESTS_PER_SECOND = 5  # Maximum 5 requests per second
DAILY_LIMIT = 1000  # Set a safe daily limit to avoid excessive charges

def load_api_key():
    """
    Load Google Places API key from environment variable.
    """
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    if not api_key:
        logger.warning("GOOGLE_PLACES_API_KEY environment variable not set. Using dummy key for testing.")
        api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key for testing
    return api_key

def load_input_data():
    """
    Load and combine data from all input files.
    """
    try:
        logger.info("Loading input data")
        
        all_dfs = []
        
        for file_path in INPUT_FILES:
            if file_path.exists():
                df = pd.read_csv(file_path)
                logger.info(f"Loaded {len(df)} records from {file_path}")
                all_dfs.append(df)
            else:
                logger.warning(f"Input file {file_path} does not exist, skipping")
        
        if not all_dfs:
            logger.error("No input files found")
            return pd.DataFrame()
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        combined_df = combined_df.drop_duplicates(subset=['name', 'latitude', 'longitude'])
        
        logger.info(f"Combined data contains {len(combined_df)} unique spots")
        
        return combined_df
    
    except Exception as e:
        logger.error(f"Error loading input data: {e}")
        raise

def find_place(api_key, name, location=None):
    """
    Use Google Places API to find a place by name and optional location.
    """
    try:
        url = f"{GOOGLE_PLACES_API_URL}/findplacefromtext/json"
        
        params = {
            'input': name,
            'inputtype': 'textquery',
            'fields': 'place_id,name,formatted_address,geometry',
            'key': api_key
        }
        
        if location and isinstance(location, tuple) and len(location) == 2:
            lat, lng = location
            if lat and lng:
                params['locationbias'] = f"point:{lat},{lng}"
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'OK':
            candidates = data.get('candidates', [])
            if candidates:
                return candidates[0]
        
        return None
    
    except Exception as e:
        logger.error(f"Error finding place '{name}': {e}")
        return None

def get_place_details(api_key, place_id):
    """
    Get detailed information about a place using its place_id.
    """
    try:
        url = f"{GOOGLE_PLACES_API_URL}/details/json"
        
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,geometry,opening_hours,rating,user_ratings_total,editorial_summary,types',
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'OK':
            return data.get('result', {})
        
        return {}
    
    except Exception as e:
        logger.error(f"Error getting place details for place_id '{place_id}': {e}")
        return {}

def enrich_data(df, api_key, limit=None):
    """
    Enrich the data with information from Google Places API.
    """
    try:
        logger.info("Enriching data with Google Places API")
        
        enriched_df = df.copy()
        
        enriched_df['google_place_id'] = ''
        enriched_df['google_address'] = ''
        enriched_df['google_latitude'] = None
        enriched_df['google_longitude'] = None
        enriched_df['google_opening_hours'] = ''
        enriched_df['google_rating'] = None
        enriched_df['google_user_ratings_total'] = None
        enriched_df['google_summary'] = ''
        enriched_df['google_types'] = ''
        
        request_count = 0
        
        for idx, row in enriched_df.iterrows():
            if limit and idx >= limit:
                break
            
            if request_count >= DAILY_LIMIT:
                logger.warning(f"Reached daily limit of {DAILY_LIMIT} requests. Stopping.")
                break
            
            name = row['name']
            lat = row.get('latitude')
            lng = row.get('longitude')
            
            logger.info(f"Processing spot {idx+1}/{len(enriched_df)}: {name}")
            
            location = (lat, lng) if pd.notna(lat) and pd.notna(lng) else None
            place = find_place(api_key, name, location)
            
            request_count += 1
            
            time.sleep(1.0 / REQUESTS_PER_SECOND)
            
            if place:
                place_id = place.get('place_id')
                enriched_df.at[idx, 'google_place_id'] = place_id
                
                enriched_df.at[idx, 'google_address'] = place.get('formatted_address', '')
                
                geometry = place.get('geometry', {})
                location = geometry.get('location', {})
                enriched_df.at[idx, 'google_latitude'] = location.get('lat')
                enriched_df.at[idx, 'google_longitude'] = location.get('lng')
                
                details = get_place_details(api_key, place_id)
                
                request_count += 1
                
                time.sleep(1.0 / REQUESTS_PER_SECOND)
                
                opening_hours = details.get('opening_hours', {})
                weekday_text = opening_hours.get('weekday_text', [])
                enriched_df.at[idx, 'google_opening_hours'] = '; '.join(weekday_text) if weekday_text else ''
                
                enriched_df.at[idx, 'google_rating'] = details.get('rating')
                enriched_df.at[idx, 'google_user_ratings_total'] = details.get('user_ratings_total')
                
                editorial_summary = details.get('editorial_summary', {})
                enriched_df.at[idx, 'google_summary'] = editorial_summary.get('overview', '')
                
                types = details.get('types', [])
                enriched_df.at[idx, 'google_types'] = ', '.join(types) if types else ''
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx+1} spots, made {request_count} API requests")
        
        logger.info(f"Enrichment complete. Made {request_count} API requests.")
        
        return enriched_df
    
    except Exception as e:
        logger.error(f"Error enriching data: {e}")
        raise

def merge_google_data(df):
    """
    Merge Google Places data with existing data, preferring Google data when available.
    """
    try:
        logger.info("Merging Google Places data with existing data")
        
        merged_df = df.copy()
        
        mask = merged_df['google_address'].notna() & (merged_df['google_address'] != '')
        merged_df.loc[mask, 'address'] = merged_df.loc[mask, 'google_address']
        
        mask = merged_df['google_latitude'].notna() & merged_df['google_longitude'].notna()
        merged_df.loc[mask, 'latitude'] = merged_df.loc[mask, 'google_latitude']
        merged_df.loc[mask, 'longitude'] = merged_df.loc[mask, 'google_longitude']
        
        mask = merged_df['google_opening_hours'].notna() & (merged_df['google_opening_hours'] != '')
        merged_df.loc[mask, 'opening_hours'] = merged_df.loc[mask, 'google_opening_hours']
        
        mask = merged_df['google_summary'].notna() & (merged_df['google_summary'] != '')
        merged_df.loc[mask, 'summary'] = merged_df.loc[mask, 'google_summary']
        
        merged_df['rating'] = merged_df['google_rating']
        merged_df['types'] = merged_df['google_types']
        
        google_cols = [col for col in merged_df.columns if col.startswith('google_')]
        merged_df = merged_df.drop(columns=google_cols)
        
        return merged_df
    
    except Exception as e:
        logger.error(f"Error merging Google data: {e}")
        raise

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Enrich tourist spot data with Google Places API')
    parser.add_argument('--limit', type=int, help='Limit the number of spots to process')
    return parser.parse_args()

def main():
    """
    Main function to enrich data with Google Places API.
    """
    try:
        args = parse_args()
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        api_key = load_api_key()
        
        df = load_input_data()
        
        if len(df) == 0:
            logger.error("No input data available")
            return pd.DataFrame()
        
        enriched_df = enrich_data(df, api_key, limit=args.limit)
        
        merged_df = merge_google_data(enriched_df)
        
        merged_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(merged_df)} enriched tourist spots to {OUTPUT_FILE}")
        
        return merged_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
