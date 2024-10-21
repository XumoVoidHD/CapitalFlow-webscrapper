from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# Define login credentials
credentials = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

with sync_playwright() as p:
    # Launch a browser (you can use 'chromium', 'firefox', or 'webkit')
    browser = p.chromium.launch(headless=False)  # Change to False to see the browser
    context = browser.new_context()

    # Open a new page
    page = context.new_page()

    # Navigate to the login page
    page.goto('https://dashboard.capitalflow.app/auth/login')

    # Using label text to fill the form (Playwright)
    page.fill('text="Email Address"', credentials['username'])
    page.fill('text="Password"', credentials['password'])

    # Click the submit button using its text
    page.click('text="Login"')

    # Wait for the main page to load
    page.wait_for_load_state('networkidle')

    # Go to the protected page
    # page.goto('https://dashboard.capitalflow.app/')

    # Get the page content
    html = page.content()

    # Optionally, parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.prettify())

    # Save to a text file
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(soup.get_text())

    # Close the browser
    # browser.close()
