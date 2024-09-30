from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import time

#     """Set up the Selenium WebDriver."""
def setup_driver():
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        exit()

#     """Open the specified URL."""
def open_url(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
    except Exception as e:
        print(f"Error opening URL {url}: {e}")
        driver.quit()
        exit()

#     """Get the maximum number of pages from the site."""
def get_max_page(driver):
    try:
        max_page_xpath = "/html/body/div/div/div[2]/div/div[2]/div[3]/div[1]/div[2]/div/button[6]"
        pages = driver.find_element(By.XPATH, max_page_xpath)
        return int(pages.text)
    except Exception as e:
        print(f"Error finding max page element: {e}")
        return 0

#     """Extract project data from the specified number of pages."""
def extract_project_data(driver, pages):
    project_data = []

    for i in range(pages):
    # for i in range(1):
        url = f"https://registry.goldstandard.org/projects?q=&page={i+1}"
        print(url)
        driver.get(url)
        time.sleep(5)

        driver.implicitly_wait(20)

        try:
            table = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div/div[2]/div[2]/div/table")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                col_data = extract_row_data(cols)
                project_data.append(col_data)

            print("Project Data:", project_data)
        except Exception as e:
            print(f"Error extracting data from page {i+1}: {e}")

    return project_data

#     """Extract URL data for description."""
def extract_row_data(cols):

    col_data = []

    for col in cols:
        cell_text = col.text.strip()
        
        if cell_text:
            if cell_text == 'VIEW':
                try:
                    link = col.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute('href')
                    col_data.append(href)
                except Exception as e:
                    col_data.append("No Link")
                    print(f"Error finding link in column: {e}")
            else:
                col_data.append(cell_text)
        else:
            try:
                img = col.find_element(By.TAG_NAME, "img")
                img_title = img.get_attribute('alt')
                col_data.append(img_title)
            except Exception as e:
                col_data.append("No Data")
                print(f"Error finding image in column: {e}")

    return col_data

final_project_data = []

#     """Get descriptions for each project."""
def get_project_descriptions(driver, project_data):

    for data in project_data:
        desc_url = data[-1]
        try:
            driver.get(desc_url)
            time.sleep(5)
            desc = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[2]/p[2]")
            data.append(desc.text)
            final_project_data.append(data)
        except Exception as e:
            data.append("No Description")
            final_project_data.append(data)
            print(f"Error fetching description from {desc_url}: {e}")

#     """Save project data to SQLite database."""
def save_to_database(final_project_data):

    try:
        conn = sqlite3.connect('projects.db')
        cursor = conn.cursor()

        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            gs_id INTEGER,
            project_details TEXT,
            status TEXT,
            sdgs TEXT,
            project_type TEXT,
            country TEXT,
            actions TEXT,
            description TEXT
        )
        ''')
        print('deleting rows from database')
        cursor.execute('DELETE FROM projects')

        cursor.executemany('''
        INSERT INTO projects (gs_id, project_details, status, sdgs, project_type, country, actions, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', final_project_data)

        conn.commit()
        print("Data has been inserted successfully!")
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    driver = setup_driver()
    
    url = "https://registry.goldstandard.org/projects?q=&page=1"
    open_url(driver, url)

    pages = get_max_page(driver)
    project_data = extract_project_data(driver, pages)
    get_project_descriptions(driver, project_data)
    print(len(final_project_data), "final_project_data")
    print(final_project_data)
    save_to_database(final_project_data)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
