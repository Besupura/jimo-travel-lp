
"""
Queries the Overpass API for tourist spots in Okinawa Prefecture and converts the results to CSV.
"""

import os
import sys
import logging
import pandas as pd
import requests
import json
from pathlib import Path
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_osm.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
OUTPUT_DIR = Path("data/interim")
OUTPUT_FILE = OUTPUT_DIR / "03_osm_spots.csv"

OKINAWA_BBOX = "24.0,122.5,27.0,131.5"

def build_overpass_query():
    """
    Build the Overpass API query for tourist spots in Okinawa.
    """
    query = f"""
    [out:json][timeout:300];
    (
      // Tourist attractions
      node["tourism"="attraction"]["name"](area:3600298220);
      way["tourism"="attraction"]["name"](area:3600298220);
      relation["tourism"="attraction"]["name"](area:3600298220);
      
      // Museums
      node["tourism"="museum"]["name"](area:3600298220);
      way["tourism"="museum"]["name"](area:3600298220);
      relation["tourism"="museum"]["name"](area:3600298220);
      
      // Theme parks
      node["tourism"="theme_park"]["name"](area:3600298220);
      way["tourism"="theme_park"]["name"](area:3600298220);
      relation["tourism"="theme_park"]["name"](area:3600298220);
      
      // Viewpoints
      node["tourism"="viewpoint"]["name"](area:3600298220);
      way["tourism"="viewpoint"]["name"](area:3600298220);
      relation["tourism"="viewpoint"]["name"](area:3600298220);
      
      // Historic sites
      node["historic"]["name"](area:3600298220);
      way["historic"]["name"](area:3600298220);
      relation["historic"]["name"](area:3600298220);
      
      // Parks
      node["leisure"="park"]["name"](area:3600298220);
      way["leisure"="park"]["name"](area:3600298220);
      relation["leisure"="park"]["name"](area:3600298220);
    );
    out body;
    >;
    out skel qt;
    """
    
    return query

def fetch_osm_data(query):
    """
    Fetch data from Overpass API.
    """
    try:
        logger.info("Fetching data from Overpass API")
        
        response = requests.post(OVERPASS_API_URL, data={"data": query})
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"Fetched {len(data.get('elements', []))} elements from Overpass API")
        
        return data
    
    except Exception as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
        raise

def process_osm_data(data):
    """
    Process the OSM data and convert to DataFrame.
    """
    try:
        logger.info("Processing OSM data")
        
        elements = data.get('elements', [])
        spots = []
        
        for element in elements:
            try:
                element_type = element.get('type')
                tags = element.get('tags', {})
                
                if 'name' not in tags:
                    continue
                
                lat, lon = None, None
                if element_type == 'node':
                    lat = element.get('lat')
                    lon = element.get('lon')
                elif element_type in ['way', 'relation']:
                    center = element.get('center', {})
                    if center:
                        lat = center.get('lat')
                        lon = center.get('lon')
                
                if lat is None or lon is None:
                    continue
                
                name = tags.get('name', '')
                name_en = tags.get('name:en', '')
                name_ja = tags.get('name:ja', '')
                
                if not name and name_en:
                    name = name_en
                elif not name and name_ja:
                    name = name_ja
                
                addr_housenumber = tags.get('addr:housenumber', '')
                addr_street = tags.get('addr:street', '')
                addr_city = tags.get('addr:city', '')
                addr_postcode = tags.get('addr:postcode', '')
                
                address_parts = []
                if addr_postcode:
                    address_parts.append(addr_postcode)
                if addr_city:
                    address_parts.append(addr_city)
                if addr_street:
                    address_parts.append(addr_street)
                if addr_housenumber:
                    address_parts.append(addr_housenumber)
                
                address = ', '.join(address_parts)
                
                opening_hours = tags.get('opening_hours', '')
                
                description = tags.get('description', '')
                if not description:
                    tourism_type = tags.get('tourism', '')
                    historic_type = tags.get('historic', '')
                    leisure_type = tags.get('leisure', '')
                    
                    if tourism_type:
                        description = f"Tourism: {tourism_type}"
                    elif historic_type:
                        description = f"Historic: {historic_type}"
                    elif leisure_type:
                        description = f"Leisure: {leisure_type}"
                
                if 'tourism' in tags:
                    category = tags['tourism']
                elif 'historic' in tags:
                    category = tags['historic']
                elif 'leisure' in tags:
                    category = tags['leisure']
                else:
                    category = ''
                
                spot = {
                    'source': 'osm',
                    'name': name,
                    'category': category,
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'summary': description,
                    'opening_hours': opening_hours,
                    'popularity_histogram': '',  # Not available in OSM
                    'osm_id': f"{element_type}/{element.get('id')}"  # Store OSM ID for reference
                }
                
                spots.append(spot)
            
            except Exception as e:
                logger.warning(f"Error processing element: {e}")
                continue
        
        spots_df = pd.DataFrame(spots)
        
        spots_df = spots_df.drop_duplicates(subset=['name', 'latitude', 'longitude'])
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error processing OSM data: {e}")
        raise

def main():
    """
    Main function to fetch and process OSM data.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        query = build_overpass_query()
        
        data = fetch_osm_data(query)
        
        spots_df = process_osm_data(data)
        
        spots_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        logger.info(f"Saved {len(spots_df)} tourist spots to {OUTPUT_FILE}")
        
        return spots_df
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
