# MOSDAC Soil Wetness Index Scraper

This Python script uses Selenium to scrape soil wetness index data from the MOSDAC website (https://mosdac.gov.in/swi/).

## Features

- Automatically navigates to the MOSDAC website
- Clicks on the Time Series panel
- Inputs user-specified longitude and latitude
- Sets start and end dates for the data range
- Submits the form and extracts the soil wetness index data

## Requirements

- Python 3.6+
- Selenium
- Webdriver Manager
- Pandas

## Installation

1. Clone this repository or download the files.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Ensure you have Chrome browser installed on your system.

## Usage

Run the script with:

```bash
python scrape_mosdac.py
```

You will be prompted to enter:
- Longitude (e.g., 77.88)
- Latitude (e.g., 23.47)
- Start date (in DD/MM/YYYY format)
- End date (in DD/MM/YYYY format)

The script will then:
1. Open Chrome and navigate to the MOSDAC website
2. Fill in the form with your inputs
3. Submit the form
4. Extract the soil wetness index data
5. Display the results (and optionally save to a CSV file)

## Notes

- The current implementation may need adjustments based on the actual structure of the website and how the data is presented.
- If the website structure changes, the XPath selectors in the script may need to be updated.
- You can uncomment the headless mode option in the script if you don't want the browser to be visible during execution. #   w e b - s c r a p e r  
 