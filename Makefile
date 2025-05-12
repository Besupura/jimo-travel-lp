# Makefile for Okinawa ETL Pipeline

# Python interpreter
PYTHON = python

# ETL scripts directory
ETL_DIR = etl/okinawa

# Data directory
DATA_DIR = data
INTERIM_DIR = $(DATA_DIR)/interim

# Output file
OUTPUT_FILE = $(DATA_DIR)/okinawa_spots_master.csv

# Create directories
$(DATA_DIR):
	mkdir -p $(DATA_DIR)

$(INTERIM_DIR):
	mkdir -p $(INTERIM_DIR)

# ETL pipeline steps
fetch_nln: $(INTERIM_DIR)
	$(PYTHON) -m $(ETL_DIR).01_fetch_nln

fetch_ok_od: $(INTERIM_DIR)
	$(PYTHON) -m $(ETL_DIR).02_fetch_ok_od

fetch_osm: $(INTERIM_DIR)
	$(PYTHON) -m $(ETL_DIR).03_fetch_osm

enrich_google: $(INTERIM_DIR)
	$(PYTHON) -m $(ETL_DIR).04_enrich_google

popular_times: $(INTERIM_DIR)
	$(PYTHON) -m $(ETL_DIR).05_popular_times

merge_clean: $(DATA_DIR)
	$(PYTHON) -m $(ETL_DIR).90_merge_clean

# Main target to run the entire ETL pipeline
okinawa_etl: fetch_nln fetch_ok_od fetch_osm enrich_google popular_times merge_clean
	@echo "ETL pipeline completed successfully!"
	@echo "Output file: $(OUTPUT_FILE)"

# Sample target to generate a sample of the data
sample: $(DATA_DIR)
	$(PYTHON) -m $(ETL_DIR).90_merge_clean --sample=10

# Clean target to remove generated files
clean:
	rm -rf $(INTERIM_DIR)
	rm -f $(OUTPUT_FILE)
	rm -f etl_*.log

.PHONY: okinawa_etl fetch_nln fetch_ok_od fetch_osm enrich_google popular_times merge_clean sample clean
