from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time

class CapitalFlowScraper:
    def __init__(self, email, password):
        self.default_list = pd.DataFrame
        self.credentials = {
            'username': email,
            'password': password
        }

    def default(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()

            page = context.new_page()

            page.goto('https://dashboard.capitalflow.app/auth/login')

            page.fill('text="Email Address"', self.credentials['username'])
            page.fill('text="Password"', self.credentials['password'])

            page.click('text="Login"')
            try:
                page.wait_for_selector('a.introjs-skipbutton', timeout=20000)
                page.click('a.introjs-skipbutton')
            except Exception as e:
                print(f"Error or timeout while waiting for skip button: {e}")

            time.sleep(5)
            self.filter(page)
            time.sleep(1)
            self.scroll(page)
            time.sleep(5)

            html = page.content()

            soup = BeautifulSoup(html, 'html.parser')

            rows = soup.find_all('tr', class_='cursor-pointer')

            data = []

            for row in rows:
                row_data = [td.get_text(strip=True) for td in row.find_all('td')]
                data.append(row_data)

            self.default_list = pd.DataFrame(data, columns=['Date', 'Symbol', 'Spot', 'Contract', 'Price', 'Premium', 'Size', 'Bid/Ask', 'Volume'])

            print(self.default_list)

            self.default_list.to_csv('cursor_pointer_data.csv', index=False)

            browser.close()

    def filter(self, page):

        odte = input("Do you want to apply '0DTE' filter? (yes/no): ").strip().lower() == 'yes'
        weeklies = input("Do you want to apply 'WEEKLIES' filter? (yes/no): ").strip().lower() == 'yes'
        swings = input("Do you want to apply 'SWINGS' filter? (yes/no): ").strip().lower() == 'yes'
        leaps = input("Do you want to apply 'LEAPS' filter? (yes/no): ").strip().lower() == 'yes'

        if odte:
            page.click('text="0DTE"')

        if weeklies:
            page.click('text="Weeklies"')

        if swings:
            page.click('text="Swings"')

        if leaps:
            page.click('text="Leaps"')



    def scroll(self, page, intervals=500, duration=10):

        scroll_step = intervals
        time_per_interval = 1 / intervals

        start_time = time.time()

        while time.time() - start_time < duration:
            for _ in range(intervals):
                page.evaluate(f'window.scrollBy(0, {scroll_step})')
                time.sleep(time_per_interval)

            if time.time() - start_time >= duration:
                break



if __name__ == "__main__":
    email = ""
    password = ""
    scraper = CapitalFlowScraper(email, password)
    scraper.default()
