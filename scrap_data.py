from bs4 import BeautifulSoup
import requests
from selenium.webdriver import Chrome, ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import sqlite3

response = requests.get(url="https://travelyupe.com/best-cafes-in-hyderabad/")
soup = BeautifulSoup(response.text,"html.parser")
cafe_names = soup.find_all(name="h2", class_="wp-block-heading")


cafes = []
cafe_locations = []
for i in cafe_names:
    try:
        cafe_names_locations = i.getText().split(",")
        cafe_titles = cafe_names_locations[0].split(")")[1]
        cafe_locations.append(cafe_names_locations[1])
        cafes.append(cafe_titles)

    except IndexError:
        try:
            cafe_names_locations = i.getText().split(" – ")
            cafe_titles = cafe_names_locations[0].split(")")[1]
            cafe_locations.append(cafe_names_locations[1])
            cafes.append(cafe_titles)
        except IndexError:
            try:
                cafe_names_locations = i.getText().split(" – ")
                cafe_titles = cafe_names_locations[0].split(")")[1]
                cafes.append(cafe_titles)
                cafe_locations.append("Secunderabad")
            except IndexError:
                pass
img_urls = []

for figure_tag in soup.find_all(class_="wp-block-image"):
    img_tag = figure_tag.find("img")
    if img_tag:
        href_attribute = img_tag.get("src")
        img_urls.append(href_attribute)

#################################################################

def initialize_driver():
    options = ChromeOptions()
    options.add_experimental_option("detach", True)
    service = Service(executable_path=r"C:\Users\banny\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = Chrome(options=options, service=service)
    return driver


# Function to search for a cafe on Google Maps and scrape its location link
def search_cafe_locations(cafes, locations):
    driver = initialize_driver()
    cafe_links = {}

    try:
        # Open Google Maps
        driver.get("https://www.google.com/maps")

        # Wait for the page to load
        time.sleep(2)

        for cafe_name,location in zip(cafes, locations):
            # Find the search input field and enter the cafe name
            print("yeah i came here")
            search_input = driver.find_element(By.XPATH, "//input[@autofocus='autofocus']")
            search_input.clear()
            searching_command = f"{cafe_name} {location}"
            search_input.send_keys(searching_command)
            print(f"length of cafes {len(cafes)}, length of locations {len(locations)}")
            print(searching_command)
            # Press Enter to search
            search_input.send_keys(Keys.ENTER)

            # Wait for the results to load
            time.sleep(5)

            # Find the first result (assuming it's the most relevant)
            location_link = driver.current_url

            # Get the location link of the cafe
            cafe_links[cafe_name] = location_link
            print(f"Location Link for {cafe_name}: {location_link}")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # Close the browser
        driver.quit()
        return cafe_links


cafe_links = search_cafe_locations(cafes, cafe_locations)

############################################################################


def create_database_table():
    # Connect to the database (creates it if not exists)
    conn = sqlite3.connect('instance/CafesofHyderabad.db')
    c = conn.cursor()

    # Create a table
    c.execute('''CREATE TABLE IF NOT EXISTS cafes (
                    cafe_name TEXT,
                    cafe_location TEXT,
                    google_map_url TEXT,
                    img_url TEXT
                )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data():
    # Connect to the database
    conn = sqlite3.connect('instance/CafesofHyderabad.db')
    c = conn.cursor()

    # Insert data into the table
    for cafe_name, cafe_location, google_map_url, img_url in zip(cafes, cafe_locations, cafe_links.values(), img_urls[:len(img_urls)-1]):
        c.execute("INSERT INTO cafes VALUES (?, ?, ?, ?)", (cafe_name, cafe_location, google_map_url, img_url))

    # Commit changes and close connection
    conn.commit()
    conn.close()

create_database_table()

# Insert data into the database
insert_data()