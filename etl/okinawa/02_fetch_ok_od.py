
"""
Fetches data from 沖縄県オープンデータ (Okinawa Prefecture Open Data, Tourist Facility List),
extracts relevant columns, and converts it to CSV.
"""

import os
import sys
import logging
import pandas as pd
import requests
from pathlib import Path
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_ok_od.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

OKINAWA_OD_API_URL = "https://data.bodik.jp/api/3/action/datastore_search"
OKINAWA_OD_RESOURCE_ID = "c5866bde-6db9-4a8c-8dac-f00b0aba8cc8"  # Resource ID for tourist facilities
OUTPUT_DIR = Path("data/interim")
OUTPUT_FILE = OUTPUT_DIR / "02_ok_od_spots.csv"

def fetch_okinawa_opendata(resource_id, limit=1000):
    """
    Fetch data from Okinawa Prefecture Open Data API.
    """
    try:
        logger.info(f"Fetching data from Okinawa Open Data API for resource {resource_id}")
        
        all_records = []
        offset = 0
        
        while True:
            params = {
                'resource_id': resource_id,
                'limit': limit,
                'offset': offset
            }
            
            response = requests.get(OKINAWA_OD_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success', False):
                logger.error(f"API returned error: {data.get('error', {})}")
                break
                
            records = data.get('result', {}).get('records', [])
            
            if not records:
                break
                
            all_records.extend(records)
            logger.info(f"Fetched {len(records)} records, total: {len(all_records)}")
            
            if len(records) < limit:
                break
                
            offset += limit
            
            time.sleep(1)
        
        return all_records
    
    except Exception as e:
        logger.error(f"Error fetching data from Okinawa Open Data API: {e}")
        raise

def process_okinawa_opendata(records):
    """
    Process the records from Okinawa Open Data API and convert to DataFrame.
    """
    try:
        logger.info(f"Processing {len(records)} records from Okinawa Open Data")
        
        df = pd.DataFrame(records)
        
        spots_df = pd.DataFrame()
        
        spots_df['source'] = 'okinawa_od'
        
        name_cols = [col for col in df.columns if '名' in col or 'name' in col.lower()]
        if name_cols:
            spots_df['name'] = df[name_cols[0]]
        else:
            spots_df['name'] = ''
            
        addr_cols = [col for col in df.columns if '住所' in col or '所在地' in col or 'address' in col.lower()]
        if addr_cols:
            spots_df['address'] = df[addr_cols[0]]
        else:
            spots_df['address'] = ''
            
        lat_cols = [col for col in df.columns if '緯度' in col or 'latitude' in col.lower()]
        lon_cols = [col for col in df.columns if '経度' in col or 'longitude' in col.lower()]
        
        if lat_cols and lon_cols:
            spots_df['latitude'] = pd.to_numeric(df[lat_cols[0]], errors='coerce')
            spots_df['longitude'] = pd.to_numeric(df[lon_cols[0]], errors='coerce')
        else:
            spots_df['latitude'] = None
            spots_df['longitude'] = None
            
        desc_cols = [col for col in df.columns if '説明' in col or '概要' in col or 'description' in col.lower()]
        if desc_cols:
            spots_df['summary'] = df[desc_cols[0]]
        else:
            spots_df['summary'] = ''
            
        hours_cols = [col for col in df.columns if '営業時間' in col or '開館時間' in col or 'hours' in col.lower()]
        if hours_cols:
            spots_df['opening_hours'] = df[hours_cols[0]]
        else:
            spots_df['opening_hours'] = ''
            
        spots_df['popularity_histogram'] = ''
        
        cat_cols = [col for col in df.columns if 'カテゴリ' in col or '分類' in col or 'category' in col.lower()]
        if cat_cols:
            spots_df['category'] = df[cat_cols[0]]
        else:
            spots_df['category'] = ''
        
        spots_df = spots_df.dropna(subset=['name'])
        
        logger.info(f"Mapped columns: {spots_df.columns.tolist()}")
        logger.info(f"Original columns: {df.columns.tolist()}")
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error processing Okinawa Open Data: {e}")
        raise

def main():
    """
    Main function to fetch and process Okinawa Open Data.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        records = fetch_okinawa_opendata(OKINAWA_OD_RESOURCE_ID)
        
        spots_df = process_okinawa_opendata(records)
        
        spots_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(spots_df)} tourist spots to {OUTPUT_FILE}")
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
