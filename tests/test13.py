from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Set up Chrome options to run the browser in headless mode (optional)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Comment this if you want to see the browser window
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize the Chrome driver using WebDriverManager to download and manage the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Replace with your login URL and credentials
login_url = 'https://dashboard.capitalflow.app/auth/login'
username = 'adam.marshall8920@gmail.com'
password = '@Aa5544163'

try:
    # Step 1: Navigate to the login page
    driver.get(login_url)
    time.sleep(3)  # Wait for the page to load

    # Step 2: Find the login form elements and submit the credentials
    username_input = driver.find_element(By.ID, "f_cf33d66c-ae29-4f3c-8542-fe75eeeb4c59")  # Change 'username' to the actual name or id of the element
    password_input = driver.find_element(By.ID, "f_eb218a3c-39c8-4c9c-af2b-ad3e9bdcee4e")  # Change 'password' to the actual name or id of the element
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")  # Adjust the XPath to match the login button

    time.sleep(100)

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    time.sleep(100)  # Allow time for login and page redirection

    # Step 3: After login, wait for JavaScript content to fully load
    time.sleep(5)  # Adjust this based on the complexity of the page

    # Step 4: Get the HTML of the loaded page
    page_html = driver.page_source

    # Step 5: Save the HTML to a file
    with open("page_content.html", "w", encoding="utf-8") as file:
        file.write(page_html)

    print("Page content saved to 'page_content.html'.")

finally:
    # Close the browser after the task is completed
    driver.quit()
