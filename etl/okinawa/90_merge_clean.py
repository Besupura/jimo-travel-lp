
"""
Merges the data from all sources, resolves conflicts, and cleans the data.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_merge_clean.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data")
INTERIM_DIR = Path("data/interim")
INPUT_FILES = [
    INTERIM_DIR / "01_nln_spots.csv",
    INTERIM_DIR / "02_ok_od_spots.csv",
    INTERIM_DIR / "03_osm_spots.csv",
    INTERIM_DIR / "04_google_enriched_spots.csv",
    INTERIM_DIR / "05_popular_times_spots.csv"
]
OUTPUT_FILE = OUTPUT_DIR / "okinawa_spots_master.csv"

OKINAWA_LAT_MIN = 24.0
OKINAWA_LAT_MAX = 27.0
OKINAWA_LON_MIN = 122.5
OKINAWA_LON_MAX = 131.5

def load_input_data():
    """
    Load data from all input files.
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
        
        merged_df = all_dfs[-1]
        
        logger.info(f"Using {len(merged_df)} records from the most complete dataset")
        
        return merged_df
    
    except Exception as e:
        logger.error(f"Error loading input data: {e}")
        raise

def clean_data(df):
    """
    Clean and standardize the data.
    """
    try:
        logger.info("Cleaning and standardizing data")
        
        cleaned_df = df.copy()
        
        cleaned_df.columns = [col.lower().strip() for col in cleaned_df.columns]
        
        required_columns = ['name', 'address', 'latitude', 'longitude', 'summary', 'opening_hours', 'popularity_histogram']
        for col in required_columns:
            if col not in cleaned_df.columns:
                cleaned_df[col] = ''
        
        cleaned_df['name'] = cleaned_df['name'].astype(str).str.strip()
        
        cleaned_df['address'] = cleaned_df['address'].astype(str).str.strip()
        
        cleaned_df['latitude'] = pd.to_numeric(cleaned_df['latitude'], errors='coerce')
        cleaned_df['longitude'] = pd.to_numeric(cleaned_df['longitude'], errors='coerce')
        
        cleaned_df['summary'] = cleaned_df['summary'].astype(str).str.strip()
        
        cleaned_df['opening_hours'] = cleaned_df['opening_hours'].astype(str).str.strip()
        
        cleaned_df['popularity_histogram'] = cleaned_df['popularity_histogram'].astype(str).str.strip()
        
        mask = (
            (cleaned_df['latitude'] >= OKINAWA_LAT_MIN) & 
            (cleaned_df['latitude'] <= OKINAWA_LAT_MAX) & 
            (cleaned_df['longitude'] >= OKINAWA_LON_MIN) & 
            (cleaned_df['longitude'] <= OKINAWA_LON_MAX)
        )
        
        valid_coords = cleaned_df['latitude'].notna() & cleaned_df['longitude'].notna()
        if valid_coords.any():
            okinawa_spots = cleaned_df[mask | ~valid_coords]
            logger.info(f"Filtered out {len(cleaned_df) - len(okinawa_spots)} spots outside of Okinawa")
            cleaned_df = okinawa_spots
        
        cleaned_df = cleaned_df.drop_duplicates(subset=['name', 'latitude', 'longitude'])
        
        cleaned_df['name'] = cleaned_df['name'].fillna('')
        cleaned_df['address'] = cleaned_df['address'].fillna('')
        cleaned_df['summary'] = cleaned_df['summary'].fillna('')
        cleaned_df['opening_hours'] = cleaned_df['opening_hours'].fillna('')
        cleaned_df['popularity_histogram'] = cleaned_df['popularity_histogram'].fillna('')
        
        cleaned_df = cleaned_df[cleaned_df['name'] != '']
        
        cleaned_df = cleaned_df.sort_values('name')
        
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        logger.info(f"Cleaned data contains {len(cleaned_df)} spots")
        
        return cleaned_df
    
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")
        raise

def add_attribution(df):
    """
    Add attribution information to the dataframe.
    """
    try:
        logger.info("Adding attribution information")
        
        attributed_df = df.copy()
        
        attributed_df['data_sources'] = 'This dataset was created using data from the following sources: '
        attributed_df['data_sources'] += '国土数値情報 P12 "観光資源" (National Land Numerical Information, Tourist Resources), '
        attributed_df['data_sources'] += '沖縄県オープンデータ「観光施設一覧」(Okinawa Prefecture Open Data, Tourist Facility List), '
        attributed_df['data_sources'] += 'OpenStreetMap (© OpenStreetMap contributors), '
        attributed_df['data_sources'] += 'Google Places API, '
        attributed_df['data_sources'] += 'and Google Maps (for popular times data).'
        
        return attributed_df
    
    except Exception as e:
        logger.error(f"Error adding attribution: {e}")
        raise

def generate_sample(df, sample_size=10):
    """
    Generate a sample of the data for testing.
    """
    try:
        logger.info(f"Generating sample of {sample_size} spots")
        
        sample_df = df.copy()
        
        if len(sample_df) > sample_size:
            sample_df = sample_df.sample(sample_size, random_state=42)
        
        sample_df = sample_df.reset_index(drop=True)
        
        return sample_df
    
    except Exception as e:
        logger.error(f"Error generating sample: {e}")
        raise

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Merge and clean tourist spot data')
    parser.add_argument('--sample', type=int, help='Generate a sample of the data with the specified number of spots')
    return parser.parse_args()

def main():
    """
    Main function to merge and clean data.
    """
    try:
        args = parse_args()
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(INTERIM_DIR, exist_ok=True)
        
        df = load_input_data()
        
        if len(df) == 0:
            logger.error("No input data available")
            return pd.DataFrame()
        
        cleaned_df = clean_data(df)
        
        attributed_df = add_attribution(cleaned_df)
        
        if args.sample:
            sample_df = generate_sample(attributed_df, args.sample)
            
            print("\nSample of Okinawa tourist spots:")
            print("=" * 80)
            for idx, row in sample_df.iterrows():
                print(f"Spot {idx+1}: {row['name']}")
                print(f"  Address: {row['address']}")
                print(f"  Coordinates: {row['latitude']}, {row['longitude']}")
                print(f"  Summary: {row['summary'][:100]}..." if len(row['summary']) > 100 else f"  Summary: {row['summary']}")
                print(f"  Opening Hours: {row['opening_hours']}")
                print(f"  Popularity: {'Yes' if row['popularity_histogram'] else 'No'}")
                print("-" * 80)
            
            sample_file = OUTPUT_DIR / "okinawa_spots_sample.csv"
            sample_df.to_csv(sample_file, index=False, encoding='utf-8')
            logger.info(f"Saved sample of {len(sample_df)} spots to {sample_file}")
            
            return sample_df
        
        attributed_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(attributed_df)} spots to {OUTPUT_FILE}")
        
        return attributed_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
