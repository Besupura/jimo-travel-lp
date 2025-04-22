# Okinawa Tourist Spots ETL Pipeline

This repository contains an ETL (Extract, Transform, Load) pipeline for generating a comprehensive dataset of major tourist spots in Okinawa Prefecture, Japan. The pipeline fetches data from multiple sources, enriches it with additional information, and merges it into a single CSV file.

## Data Sources

The ETL pipeline uses the following data sources:

1. **国土数値情報 P12 "観光資源"** (National Land Numerical Information, Tourist Resources)
   - Source: [https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P12-v2_2.html](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P12-v2_2.html)
   - Contains basic information about tourist spots in Japan, including Okinawa Prefecture.

2. **沖縄県オープンデータ「観光施設一覧」** (Okinawa Prefecture Open Data, Tourist Facility List)
   - Source: Okinawa Prefecture Open Data API
   - Contains information about tourist facilities in Okinawa Prefecture.

3. **OpenStreetMap** (via Overpass API)
   - Source: [https://wiki.openstreetmap.org/wiki/Overpass_API](https://wiki.openstreetmap.org/wiki/Overpass_API)
   - Contains crowd-sourced information about tourist spots, museums, theme parks, viewpoints, historic sites, and parks in Okinawa Prefecture.

4. **Google Places API**
   - Source: [https://developers.google.com/maps/documentation/places/web-service](https://developers.google.com/maps/documentation/places/web-service)
   - Used to enrich the data with additional information such as address, opening hours, and summary.

5. **Google Popular Times** (unofficial scraping)
   - Source: Google Maps
   - Used to obtain popularity histograms for tourist spots.

## Prerequisites

- Python 3.8 or higher
- Make (for running the Makefile)
- Chrome browser and ChromeDriver (for scraping Google Popular Times)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Besupura/jimo-travel-lp.git
   cd jimo-travel-lp
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys (see the "API Keys Configuration" section below).

## API Keys Configuration

The ETL pipeline requires API keys for the following services:

### Google Places API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the "Places API" for your project.
4. Create an API key.
5. Set the API key as an environment variable:
   ```bash
   export GOOGLE_PLACES_API_KEY="your_api_key_here"
   ```

   Alternatively, you can create a `.env` file in the repository root with the following content:
   ```
   GOOGLE_PLACES_API_KEY=your_api_key_here
   ```

### Google Popular Times (Unofficial Scraping)

The ETL pipeline uses Selenium with Chrome to scrape Google Popular Times data. You need to install Chrome and ChromeDriver:

1. Install Chrome browser if you don't have it already.
2. Download ChromeDriver from [https://sites.google.com/a/chromium.org/chromedriver/downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads).
3. Make sure ChromeDriver is in your PATH or specify its location in the `05_popular_times.py` script.

## Running the ETL Pipeline

To run the entire ETL pipeline, use the following command:

```bash
make okinawa_etl
```

This will execute all the ETL scripts in the correct order and generate the final CSV file at `data/okinawa_spots_master.csv`.

### Running Individual Steps

You can also run individual steps of the ETL pipeline:

```bash
make fetch_nln        # Fetch data from National Land Numerical Information
make fetch_ok_od      # Fetch data from Okinawa Prefecture Open Data
make fetch_osm        # Fetch data from OpenStreetMap
make enrich_google    # Enrich data with Google Places API
make popular_times    # Scrape Google Popular Times data
make merge_clean      # Merge and clean the data
```

### Generating a Sample

To generate a sample of the data (10 spots), use the following command:

```bash
make sample
```

This will print a sample of the data to the console and save it to `data/okinawa_spots_sample.csv`.

### Cleaning Up

To clean up the generated files, use the following command:

```bash
make clean
```

## Output Format

The final CSV file (`data/okinawa_spots_master.csv`) contains the following columns:

- `name`: Name of the tourist spot
- `address`: Address of the tourist spot
- `latitude`: Latitude coordinate
- `longitude`: Longitude coordinate
- `summary`: Summary or description of the tourist spot
- `opening_hours`: Opening hours of the tourist spot
- `popularity_histogram`: Popularity histogram data (busiest times)
- `data_sources`: Attribution information for the data sources

## Rate Limiting and Usage Considerations

The ETL pipeline respects the usage limits and licensing terms of each data source:

- **Google Places API**: The pipeline implements a delay between requests to avoid being rate-limited. By default, it's limited to 5 requests per second and 1000 requests per run.
- **Google Popular Times**: The pipeline implements a random delay between 5 and 15 seconds between requests to avoid overloading the server. By default, it's limited to 100 requests per run.

## License and Attribution

This ETL pipeline and the resulting dataset are provided for educational and research purposes only. When using the dataset, please provide proper attribution to the original data sources:

- 国土数値情報 P12 "観光資源" (National Land Numerical Information, Tourist Resources)
- 沖縄県オープンデータ「観光施設一覧」(Okinawa Prefecture Open Data, Tourist Facility List)
- OpenStreetMap (© OpenStreetMap contributors)
- Google Places API
- Google Maps (for popular times data)

## Troubleshooting

### Missing Data

If some of the data sources are unavailable or return no results, the pipeline will continue with the available data. Check the log files (`etl_*.log`) for more information.

### API Key Issues

If you encounter issues with the Google Places API, make sure your API key is correctly set and has the necessary permissions. Also, check if you've exceeded your daily quota.

### Scraping Issues

If you encounter issues with scraping Google Popular Times data, make sure Chrome and ChromeDriver are correctly installed and configured. Also, check if Google has changed their website structure, which might require updating the scraping code.
