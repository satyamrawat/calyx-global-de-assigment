# calyx-global-de-assigment
# Project Web Scraper

This project is a web scraper that collects project data from the Gold Standard registry. The project utilizes three different methodologies:

Selenium: Used for web automation and data extraction. File web_scraper.py
API Calls: Employed to retrieve data. File assignment_api.py
Scrapy Framework: Utilized for efficient web scraping.


## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3 installed on your machine.

## Installation
To install the required packages, it's recommended to use a virtual environment. You can install the packages using pip as follows:

For the Selenium approach:
pip install -r requirements_selenium.txt

For the API approach:
pip install -r requirements_api.txt

For the Scrapy framework:
cd assignment_scrapy
pip install -r requirements_scrapy.txt
- To run scrapy spide use 
scrapy crawl gold_standard -o projects.json

Note: I understand that having three separate requirements.txt files isn't the best practice, but we've created them this way for ease of use.
