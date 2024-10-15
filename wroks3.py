from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
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

    time.sleep(10)

    html = page.content()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all rows with class 'cursor-pointer'
    rows = soup.find_all('tr', class_='cursor-pointer')

    # Prepare a list to store the extracted data
    data = []

    for row in rows:
        # Extract text from each <td> within the row
        row_data = [td.get_text(strip=True) for td in row.find_all('td')]
        data.append(row_data)

    # Convert the list of data to a pandas DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Symbol', 'Spot', 'Contract', 'Price', 'Premium', 'Size', 'Bid/Ask', 'Volume'])

    # Print or save the DataFrame
    print(df)

    # Save the DataFrame to a CSV file
    df.to_csv('cursor_pointer_data.csv', index=False)


