from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

credentials = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    page.goto('https://dashboard.capitalflow.app/auth/login')

    page.fill('text="Email Address"', credentials['username'])
    page.fill('text="Password"', credentials['password'])

    page.click('text="Login"')


    try:
        page.wait_for_selector('a.introjs-skipbutton', timeout=20000)
        page.click('a.introjs-skipbutton')
        print("Intro skip button clicked.")
    except Exception as e:
        print(f"Error or timeout while waiting for skip button: {e}")

    # page.wait_for_load_state('networkidle')

    time.sleep(10)

    html = page.content()

    soup = BeautifulSoup(html, 'html.parser')
    print(soup.prettify())

    # Save to a text file
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(soup.get_text())

    browser.close()
