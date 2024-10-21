import pandas as pd
import streamlit as st
import time
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

df = pd.DataFrame()
class CapitalFlowScraper:
    def __init__(self, email, password):
        self.default_list = pd.DataFrame()
        self.credentials = {
            'username': email,
            'password': password
        }

    async def default(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            page = await context.new_page()

            await page.goto('https://dashboard.capitalflow.app/auth/login')

            await page.fill('input[name="email"]', self.credentials['username'])
            await page.fill('input[name="password"]', self.credentials['password'])

            await page.click('text="Login"')
            try:
                await page.wait_for_selector('a.introjs-skipbutton', timeout=20000)
                await page.click('a.introjs-skipbutton')
            except Exception as e:
                print(f"Error or timeout while waiting for skip button: {e}")

            await asyncio.sleep(5)
            await self.scroll(page)
            await asyncio.sleep(5)

            html = await page.content()

            soup = BeautifulSoup(html, 'html.parser')

            rows = soup.find_all('tr', class_='cursor-pointer')

            data = []

            for row in rows:
                row_data = [td.get_text(strip=True) for td in row.find_all('td')]
                data.append(row_data)

            self.default_list = pd.DataFrame(data, columns=['Date', 'Symbol', 'Spot', 'Contract', 'Price', 'Premium', 'Size', 'Bid/Ask', 'Volume'])
            df = self.default_list
            print(self.default_list)

            self.default_list.to_csv('cursor_pointer_data.csv', index=False)

            await browser.close()

    async def scroll(self, page, intervals=500, duration=10):
        scroll_step = intervals
        time_per_interval = 1 / intervals

        start_time = time.time()

        while time.time() - start_time < duration:
            for _ in range(intervals):
                await page.evaluate(f'window.scrollBy(0, {scroll_step})')
                await asyncio.sleep(time_per_interval)

            if time.time() - start_time >= duration:
                break

# Background async runner
async def run_scraper(email, password):
    scraper = CapitalFlowScraper(email, password)
    await scraper.default()



# Streamlit app interface
def main():
    st.title("CapitalFlow Scraper")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Start Scraping"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_scraper(email, password))

        st.write("Scraping started asynchronously...")
        st.write(df)

if __name__ == "__main__":
    main()
