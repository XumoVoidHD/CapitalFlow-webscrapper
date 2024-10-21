import streamlit as st
from multiprocessing import Process, Queue
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime

class CapitalFlowScraper:
    def __init__(self, email, password, queue):
        self.default_list = pd.DataFrame()
        self.credentials = {
            'username': email,
            'password': password
        }
        self.queue = queue

    def default(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
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
                self.queue.put(self.default_list)
                self.default_list.to_csv('wow.csv', index=False)

                browser.close()
                return self.default_list
        except Exception as e:
            self.queue.put(f"An error occurred: {e}")

    def filter(self, page):
        # Check for the filters using hardcoded logic
        odte, weeklies, swings, leaps = True, True, True, True

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

# Function to run the scraper in a separate process
def run_scraper(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    df = scraper.default()
    print(df)
# Streamlit UI
def main():
    st.title("CapitalFlow Scraper")

    # Input fields for email and password
    email = st.text_input("Enter your email:", type="default")
    password = st.text_input("Enter your password:", type="password")

    if st.button("Start Scraping"):
        if email and password:
            # Create a Queue for communication between processes
            queue = Queue()

            # Create and start a separate process for the scraper
            process = Process(target=run_scraper, args=(email, password, queue))
            process.start()

            # Wait for results from the queue
            while True:
                if not queue.empty():
                    result = queue.get()
                    if isinstance(result, pd.DataFrame):
                        st.success("Scraping completed successfully!")
                        break
                    else:
                        st.error(result)
                        break

                if not process.is_alive():
                    break

            process.join()
        else:
            st.error("Please provide both email and password.")

if __name__ == "__main__":
    main()

    df = pd.read_csv("wow.csv")

    symbols = st.sidebar.multiselect("Exclude Symbol(s)", options=df['Symbol'].unique(), default=[])

    if 'custom_spot' not in st.session_state:
        st.session_state.custom_spot = 1.0

    if 'custom_price' not in st.session_state:
        st.session_state.custom_price = 1.0

    if 'custom_premium' not in st.session_state:
        st.session_state.custom_premium = 1.0

    if 'custom_volume' not in st.session_state:
        st.session_state.custom_volume = 1

    if 'custom_size' not in st.session_state:
        st.session_state.custom_size = 1

    if 'filter_date' not in st.session_state:
        st.session_state.filter_date = datetime.today().date()

    if 'filter_time' not in st.session_state:
        st.session_state.filter_time = datetime.now().time()

    st.session_state.custom_spot = st.sidebar.number_input("Spot Limit", min_value=1.0, max_value=5000.0,
                                                           value=st.session_state.custom_spot, step=0.01)
    st.session_state.custom_price = st.sidebar.number_input("Price Limit", min_value=1.0, max_value=5000.0,
                                                            value=st.session_state.custom_price, step=0.01)
    st.session_state.custom_premium = st.sidebar.number_input("Premium Limit", min_value=1.0,
                                                              max_value=999999999999999.0,
                                                              value=st.session_state.custom_premium, step=0.01)
    st.session_state.custom_volume = st.sidebar.number_input("Volume Limit", min_value=1,
                                                             max_value=9999999999,
                                                             value=st.session_state.custom_volume, step=1)
    st.session_state.custom_size = st.sidebar.number_input("Size Limit", min_value=1,
                                                           max_value=9999999999,
                                                           value=st.session_state.custom_size, step=1)

    st.session_state.filter_date = st.sidebar.date_input("Filter before date", value=st.session_state.filter_date)
    st.session_state.filter_time = st.sidebar.time_input("Filter before time", value=st.session_state.filter_time)

    filter_datetime = datetime.combine(st.session_state.filter_date, st.session_state.filter_time)

    df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%y, %I:%M:%S %p")

    df['Spot'] = df['Spot'].replace({'\$': '', ',': '', '--': None}, regex=True)
    df['Spot'] = pd.to_numeric(df['Spot'], errors='coerce')

    df['Price'] = df['Price'].replace({'\$': '', ',': '', '--': None}, regex=True)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    df['Premium'] = df['Premium'].replace({'\$': '', ',': '', '--': None}, regex=True)
    df['Premium'] = pd.to_numeric(df['Premium'], errors='coerce')

    df['Volume'] = df['Volume'].replace({',': '', '--': None}, regex=True)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

    df['Size'] = df['Size'].replace({',': '', '--': None}, regex=True)
    df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

    filtered_df = df[~df['Symbol'].isin(symbols)]
    filtered_df = filtered_df[filtered_df['Date'] < filter_datetime]
    filtered_df = filtered_df[filtered_df['Spot'] >= st.session_state.custom_spot]
    filtered_df = filtered_df[filtered_df['Price'] >= st.session_state.custom_price]
    filtered_df = filtered_df[filtered_df['Premium'] >= st.session_state.custom_premium]
    filtered_df = filtered_df[filtered_df['Volume'] >= st.session_state.custom_volume]
    filtered_df = filtered_df[filtered_df['Size'] >= st.session_state.custom_size]

    filtered_df['Spot'] = filtered_df['Spot'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')
    filtered_df['Price'] = filtered_df['Price'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')
    filtered_df['Premium'] = filtered_df['Premium'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')

    st.write("Filtered Data (Symbols Excluded, Spot, Price, Premium, Volume, Size, and Date-Time Filtered):")
    st.write(filtered_df.reset_index(drop=True))
