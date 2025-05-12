# Jimo Travel LP - Okinawa Tourism Dataset

A comprehensive dataset of major tourist attractions in Okinawa Prefecture, Japan, covering key information points including facility details, visitor statistics, and review analysis.

## Dataset Overview

This dataset contains information on 120+ tourist attractions across Okinawa Prefecture, including Okinawa Island and surrounding islands. The data includes:

- Facility names (Japanese & English)
- Location information (address & coordinates)
- Opening hours by day of the week
- Closing days/holidays
- Main highlights & features
- Annual visitor numbers
- Review counts & ratings from multiple platforms
- Top positive & negative keywords from reviews
- Last updated date

## Data Acquisition Process

### Data Sources

The dataset was compiled using the following sources:

1. **Official Tourism Organizations**:
   - Japan National Tourism Organization (JNTO)
   - Okinawa Convention & Visitors Bureau (OCVB)
   - Okinawa Prefecture Tourism Department
   - Municipal tourism departments

2. **Official Statistics**:
   - Okinawa Prefecture's "Inbound Tourist Statistics"
   - Annual reports from facility managers
   - Government tourism statistics

3. **Review Platforms**:
   - Google Maps
   - TripAdvisor
   - X (formerly Twitter) hashtag search
   - Tabelog

### Methodology

The data collection process followed these steps:

1. **Generate List of Tourist Spots**:
   - Obtained official lists from JNTO, OCVB, and municipal tourism departments
   - Supplemented with Google Maps Places API search for "tourist_attraction" type
   - Merged and deduplicated results to create a comprehensive list

2. **Collect Opening Hours and Holidays**:
   - Prioritized structured data (schema.org/JSON-LD) from official websites
   - Used Google Places Details API as fallback
   - Normalized data to consistent format

3. **Gather Annual Visitor Numbers**:
   - Parsed PDFs from Okinawa Prefecture's tourism statistics
   - Extracted data from annual reports of facility managers
   - Marked unavailable data as "Unknown" with explanatory remarks

4. **Acquire Review Counts and Ratings**:
   - Collected data from Google Maps, TripAdvisor, X, and Tabelog
   - Implemented rate limiting to avoid API restrictions
   - Saved raw responses in the `/raw` directory

5. **Extract Keywords from Reviews**:
   - Performed Japanese morphological analysis on review texts
   - Calculated TF-IDF to identify significant terms
   - Extracted top 5 positive and negative keywords for each attraction

### Data Provenance

- Data acquisition date: April 22, 2025
- Each data point includes its source URL and acquisition date
- Raw data is preserved in the `/raw` directory for reproducibility

## Dataset Structure

The final dataset is available as a CSV file in the `/data` directory:
- `okinawa_tourism_20250422.csv`

The dataset includes the following columns:
- Facility Name (Japanese & English)
- Location (Address & Latitude/Longitude)
- Opening Hours (by day of the week)
- Closing Days/Holidays
- Main Highlights & Features
- Annual Visitors & Source
- Review Counts & Ratings (Google Maps, TripAdvisor, X, Tabelog)
- Top 5 Positive & Negative Keywords
- Last Updated Date

## Usage

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('data/okinawa_tourism_20250422.csv')

# View basic information
print(f"Number of attractions: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Example: Find attractions with highest Google Maps ratings
top_rated = df.sort_values('google_maps_rating', ascending=False).head(10)
print(top_rated[['name_en', 'google_maps_rating', 'google_maps_reviews']])
```

## Data Quality

- Number of attractions: 120
- Missing rate for annual visitors: 30.83% (below the 40% threshold)
- Total number of reviews collected: 614,967

## License

This dataset is provided under the Creative Commons Attribution 4.0 International License (CC BY 4.0). You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

The underlying data may be subject to the terms of service of the original data sources.
