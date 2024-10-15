from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

credentials = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
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

    time.sleep(10)

    html = page.content()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all elements with class 'cursor-pointer'
    cursor_pointer_elements = soup.find_all(class_='cursor-pointer')
    print(cursor_pointer_elements)

    # Store the text of each instance in a list
    cursor_pointer_list = [element.get_text(strip=True) for element in cursor_pointer_elements]

    # Print or save the list
    print(cursor_pointer_list)

    # Save the raw HTML to a text file
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(soup.get_text())

    # Save the cursor-pointer list to a separate file
    with open('cursor_pointer_elements.txt', 'w', encoding='utf-8') as file:
        for item in cursor_pointer_list:
            file.write(f"{item}\n")

    browser.close()
