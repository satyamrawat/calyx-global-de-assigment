import requests
import time
import sqlite3
from ratelimit import limits, sleep_and_retry
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
API_URL = "https://public-api.goldstandard.org/projects"
DB_PATH = 'projects_api.db'

# Headers (adjust according to the API documentation if needed)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

KEYS_TO_EXTRACT = ["id", "sustaincert_id", "name", "status", "type", "country", "sustaincert_url", "description"]

# Define rate limits
REQUESTS_LIMIT = 8
WAIT_TIME = 30
MAX_PAGES = 12

# Set up rate limiting and retry mechanism
@sleep_and_retry
@limits(calls=REQUESTS_LIMIT, period=WAIT_TIME)
def make_request(page):
    """Makes the request to the API with pagination"""
    try:
        response = requests.get(API_URL, params={'q': '', 'page': page}, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        logging.error(f"Request failed: {err}")
        return None


def extract_filtered_data(data):
    """Extracts specific keys from the response"""
    return [[d.get(key) for key in KEYS_TO_EXTRACT] for d in data if isinstance(d, dict)]


def save_to_database(project_data):
    """Saves the extracted data to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                gs_id INTEGER,
                project_details TEXT,
                status TEXT,
                project_type TEXT,
                country TEXT,
                actions TEXT,
                description TEXT
            )
        ''')

        # Clear old data
        logging.info("Deleting old data from the database...")
        cursor.execute('DELETE FROM projects')

        # Insert new data
        cursor.executemany('''
            INSERT INTO projects (id, gs_id, project_details, status, project_type, country, actions, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', project_data)

        conn.commit()
        logging.info("Data has been inserted successfully!")
    except sqlite3.Error as db_err:
        logging.error(f"Database error: {db_err}")
    finally:
        if conn:
            conn.close()


def main():
    """Main function to retrieve API data and store it in the database"""
    all_projects = []
    page = 1

    while True:
        logging.info(f"Fetching page {page}...")
        response = make_request(page)

        if response and response.status_code == 200:
            data = response.json()
            if not data:
                logging.info("Received an empty data list. Exiting.")
                break

            filtered_data_list = extract_filtered_data(data)
            all_projects.extend(filtered_data_list)

            logging.info(f"Page {page} processed. Total projects retrieved: {len(all_projects)}")
            page += 1

        elif response and response.status_code == 429:
            # Handle rate limit error
            logging.warning("Rate limit exceeded. Retrying after waiting...")
        else:
            logging.error(f"Failed to retrieve data. Status code: {response.status_code if response else 'No response'}")
            break

    # Output total number of projects retrieved
    logging.info(f"Total projects retrieved: {len(all_projects)}")

    # Save to database if any projects were retrieved
    if all_projects:
        save_to_database(all_projects)


if __name__ == "__main__":
    main()