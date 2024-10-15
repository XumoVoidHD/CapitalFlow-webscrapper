from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)

# Provide the path to your ChromeDriver
chrome_driver_path = '/path/to/chromedriver'  # Update this to the correct path

# Start the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Access the login page
login_url = "https://dashboard.capitalflow.app/auth/login"
driver.get(login_url)

# Fill in login form
driver.find_element(By.NAME, "Email Address").send_keys("adam.marshall8920@gmail.com")
driver.find_element(By.NAME, "Password").send_keys("@Aa5544163")
driver.find_element(By.XPATH, "//button[@type='Login']").click()

# Wait for the login to complete
time.sleep(5)

# Access the protected URL
protected_url = "https://dashboard.capitalflow.app/"
driver.get(protected_url)

# Give time for the page to fully load, including XHR data
time.sleep(5)

# Get the full page source (including all dynamically loaded content)
page_source = driver.page_source
print(page_source)

# Close the browser
driver.quit()
