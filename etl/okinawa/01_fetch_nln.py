
"""
Fetches data from 国土数値情報 P12 (National Land Numerical Information, Tourist Resources),
extracts Okinawa Prefecture data, and converts it to CSV.
"""

import os
import sys
import logging
import zipfile
import tempfile
import pandas as pd
import requests
from pathlib import Path
import xml.etree.ElementTree as ET
import geopandas as gpd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_nln.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

NLN_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/P12/P12-14/P12-14_47_GML.zip"
OKINAWA_PREF_CODE = "47"
OUTPUT_DIR = Path("data/interim")
OUTPUT_FILE = OUTPUT_DIR / "01_nln_spots.csv"

def download_nln_data(url, output_dir):
    """
    Download the National Land Numerical Information data.
    """
    try:
        logger.info(f"Downloading data from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)
            logger.info(f"Extracted files to {extract_dir}")
        
        os.unlink(temp_path)
        
        return extract_dir
    except Exception as e:
        logger.error(f"Error downloading or extracting data: {e}")
        raise

def parse_gml_data(extract_dir):
    """
    Parse the GML data and extract tourist spots in Okinawa.
    """
    try:
        logger.info("Parsing GML data")
        
        gml_files = list(Path(extract_dir).glob("**/*.shp"))
        if not gml_files:
            gml_files = list(Path(extract_dir).glob("**/*.xml"))
            if not gml_files:
                raise FileNotFoundError("No GML or SHP files found in the extracted data")
        
        gml_file = gml_files[0]
        logger.info(f"Found GML/SHP file: {gml_file}")
        
        if gml_file.suffix.lower() == '.shp':
            gdf = gpd.read_file(gml_file)
            if 'P12_001' in gdf.columns:  # Prefecture code column
                gdf = gdf[gdf['P12_001'] == OKINAWA_PREF_CODE]
            
            spots_df = pd.DataFrame({
                'source': 'nln',
                'name': gdf.get('P12_004', ''),  # Tourist spot name
                'category': gdf.get('P12_005', ''),  # Category
                'address': gdf.get('P12_006', ''),  # Address
                'latitude': gdf.geometry.y,
                'longitude': gdf.geometry.x,
                'summary': gdf.get('P12_007', ''),  # Description
                'opening_hours': '',  # Not available in this dataset
                'popularity_histogram': ''  # Not available in this dataset
            })
            
        else:
            tree = ET.parse(gml_file)
            root = tree.getroot()
            
            ns = {'gml': 'http://www.opengis.net/gml', 'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app'}
            
            spots = []
            for feature in root.findall('.//ksj:TouristSpot', ns):
                try:
                    pref_code = feature.find('.//ksj:prefectureCd', ns)
                    if pref_code is not None and pref_code.text == OKINAWA_PREF_CODE:
                        name = feature.find('.//ksj:touristSpotName', ns)
                        category = feature.find('.//ksj:touristSpotCd', ns)
                        address = feature.find('.//ksj:address', ns)
                        description = feature.find('.//ksj:description', ns)
                        
                        point = feature.find('.//gml:Point', ns)
                        if point is not None:
                            coords = point.find('.//gml:coordinates', ns)
                            if coords is not None:
                                lon, lat = coords.text.split(',')
                                
                                spots.append({
                                    'source': 'nln',
                                    'name': name.text if name is not None else '',
                                    'category': category.text if category is not None else '',
                                    'address': address.text if address is not None else '',
                                    'latitude': float(lat),
                                    'longitude': float(lon),
                                    'summary': description.text if description is not None else '',
                                    'opening_hours': '',  # Not available in this dataset
                                    'popularity_histogram': ''  # Not available in this dataset
                                })
                except Exception as e:
                    logger.warning(f"Error parsing feature: {e}")
                    continue
            
            spots_df = pd.DataFrame(spots)
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error parsing GML data: {e}")
        raise

def main():
    """
    Main function to fetch and process NLN data.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        extract_dir = download_nln_data(NLN_URL, OUTPUT_DIR)
        
        spots_df = parse_gml_data(extract_dir)
        
        spots_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(spots_df)} tourist spots to {OUTPUT_FILE}")
        
        import shutil
        shutil.rmtree(extract_dir)
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
