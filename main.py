import streamlit as st
from multiprocessing import Process, Queue
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from discord_bot import send_message
import os
import json

token = " "
user = " "
url = " "

if 'email' not in st.session_state:
    st.session_state['email'] = ''
if 'password' not in st.session_state:
    st.session_state['password'] = ''
if 'call' not in st.session_state:
    st.session_state['call'] = 0
if 'put' not in st.session_state:
    st.session_state['put'] = 0
if 'signal' not in st.session_state:
    st.session_state['signal'] = None


class CapitalFlowScraper:
    def __init__(self, email, password, queue):
        self.default_list = pd.DataFrame()
        self.credentials = {
            'username': email,
            'password': password
        }
        self.queue = queue
        self.signal = None
        self.call = None
        self.put = None

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

                sentiment_element = soup.find('p', {
                    'data-hint': 'Based on received call and put premium this will show current bullish or bearish sentiment.'})
                if sentiment_element:
                    sentiment_text = sentiment_element.get_text(strip=True)
                    print(f"Sentiment: {sentiment_text}")
                    self.signal = sentiment_text
                else:
                    print("Sentiment not found")
                    self.signal = "Unknown"

                call_premium_element = soup.find('p', {
                    'data-hint': 'Total call premium on executed contracts observed over $2.5k.'})
                if call_premium_element:
                    call_premium = float(call_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                    print(f"Call: {call_premium}")
                    self.call = call_premium
                else:
                    print("Call not found")

                put_premium_element = soup.find('p', {
                    'data-hint': 'Total put premium on executed contracts observed over $2.5k.'})
                if put_premium_element:
                    put_premium = float(put_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                    print(f"Put: {put_premium}")
                    self.put = put_premium
                else:
                    print("Put not found")

                if self.signal == "Unknown" and call_premium and put_premium:
                    if put_premium > call_premium:
                        sentiment = "Bearish"
                    else:
                        sentiment = "Bullish"
                    self.signal = sentiment

                rows = soup.find_all('tr', class_='cursor-pointer')
                data = []
                for row in rows:
                    row_data = [td.get_text(strip=True) for td in row.find_all('td')]
                    data.append(row_data)

                self.default_list = pd.DataFrame(data,
                                                 columns=['Date', 'Symbol', 'Spot', 'Contract', 'Price', 'Premium',
                                                          'Size', 'Bid/Ask', 'Volume'])

                self.queue.put(self.default_list)
                self.queue.put(self.signal)
                self.queue.put(self.call)
                self.queue.put(self.put)

                self.default_list["Call/Put"] = 0.0
                for i in range(0, len(self.default_list)):
                    if 'C' in str(self.default_list['Contract'].iloc[i]):
                        self.default_list['Call/Put'].iloc[i] = "Call"
                    else:
                        self.default_list['Call/Put'].iloc[i] = "Put"

                cols = list(self.default_list.columns)
                cols.remove("Call/Put")
                cols.insert(cols.index('Contract') + 1, "Call/Put")
                self.default_list = self.default_list[cols]

                columns_to_replace = ['Spot', 'Price', 'Premium', 'Volume', 'Size']
                self.default_list[columns_to_replace] = self.default_list[columns_to_replace].replace({'--': -1})

                for i in range(0, len(self.default_list)):
                    if str(self.default_list['Volume'].iloc[i]).endswith("K"):
                        self.default_list['Volume'].iloc[i] = round(
                            float(self.default_list['Volume'].iloc[i][:-1]) * 1000, 2)
                    elif str(self.default_list['Volume'].iloc[i]).endswith("M"):
                        self.default_list['Volume'].iloc[i] = round(
                            float(self.default_list['Volume'].iloc[i][:-1]) * 1000000, 2)
                    elif str(self.default_list['Volume'].iloc[i]) == "--":
                        self.default_list['Volume'].iloc[i] = -1

                for i in range(0, len(self.default_list)):
                    if str(self.default_list['Size'].iloc[i]).endswith("K"):
                        self.default_list['Size'].iloc[i] = round(float(self.default_list['Size'].iloc[i][:-1]) * 1000,
                                                                  2)
                    elif str(self.default_list['Size'].iloc[i]).endswith("M"):
                        self.default_list['Size'].iloc[i] = round(
                            float(self.default_list['Size'].iloc[i][:-1]) * 1000000, 2)
                    elif str(self.default_list['Size'].iloc[i]) == "--":
                        self.default_list['Size'].iloc[i] = -1

                print(self.default_list)
                self.default_list.to_excel('wow.xlsx', index=False)

                json_file = "signal_call_put_data.json"
                with open(json_file, "w") as file:
                    json.dump({
                        "signal": self.signal,
                        "put": self.put,
                        "call": self.call
                    }, file)

                json_file = "prev_signal_data.json"
                with open(json_file, "w") as file:
                    json.dump({"prev_signal": self.signal}, file)

                browser.close()

                return self.default_list, self.signal, self.call, self.put

        except Exception as e:
            self.queue.put(f"An error occurred: {e}")

    def filter(self, page):
        odte, weeklies, swings, leaps = False, False, False, False

        if odte:
            page.click('text="0DTE"')

        if weeklies:
            page.click('text="Weeklies"')

        if swings:
            page.click('text="Swings"')

        if leaps:
            page.click('text="Leaps"')

    def scroll(self, page, intervals=1000, duration=20):
        scroll_step = intervals
        time_per_interval = 1 / intervals

        start_time = time.time()

        while time.time() - start_time < duration:
            for _ in range(intervals):
                page.evaluate(f'window.scrollBy(0, {scroll_step})')
                time.sleep(time_per_interval)

            if time.time() - start_time >= duration:
                break

    def notif(self):
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

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                sentiment_element = soup.find('p', {
                    'data-hint': 'Based on received call and put premium this will show current bullish or bearish sentiment.'})
                if sentiment_element:
                    sentiment_text = sentiment_element.get_text(strip=True)
                    st.session_state['signal'] = sentiment_text
                else:
                    print("Sentiment element not found based on data-hint.")
                    st.session_state['signal'] = "Unknown"

                call_premium_element = soup.find('p', {
                    'data-hint': 'Total call premium on executed contracts observed over $2.5k.'})
                if call_premium_element:
                    call_premium = float(call_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                    st.session_state['call'] = call_premium
                else:
                    print("Call premium element not found based on data-hint.")

                put_premium_element = soup.find('p', {
                    'data-hint': 'Total put premium on executed contracts observed over $2.5k.'})
                if put_premium_element:
                    put_premium = float(put_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                    st.session_state['put'] = put_premium
                else:
                    print("Put premium element not found based on data-hint.")

                if st.session_state['signal'] == "Unknown" and st.session_state['call'] and st.session_state['put']:
                    if st.session_state['put'] > st.session_state['call']:
                        sentiment = "Bearish"
                    else:
                        sentiment = "Bullish"
                    print(f"Sentiment determined by comparison: {sentiment}")
                    st.session_state['signal'] = sentiment

                pro = Process(target=send_msg, args=(sentiment_text, call_premium, put_premium))
                pro.start()

                browser.close()

                print(f"Signal: {st.session_state['signal']}")
                print(f"Total Call Premium: ${st.session_state['call']}")
                print(f"Total Put Premium: ${st.session_state['put']}")

        except Exception as e:
            st.session_state['error'] = f"An error occurred: {e}"

    def signal_gen(self):
        try:
            json_file = "prev_signal_data.json"
            if os.path.exists(json_file):
                with open(json_file, "r") as file:
                    data = json.load(file)
                    prev_signal = data.get("prev_signal", "Unknown")
            else:
                prev_signal = "Unknown"

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

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                sentiment_element = soup.find('p', {
                    'data-hint': 'Based on received call and put premium this will show current bullish or bearish sentiment.'})
                if sentiment_element:
                    sentiment_text = sentiment_element.get_text(strip=True)
                    current_signal = sentiment_text
                else:
                    print("Sentiment element not found based on data-hint.")
                    current_signal = "Unknown"

                call_premium_element = soup.find('p', {
                    'data-hint': 'Total call premium on executed contracts observed over $2.5k.'})
                if call_premium_element:
                    call_premium = float(call_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                else:
                    print("Call premium element not found based on data-hint.")
                    call_premium = 0.0

                put_premium_element = soup.find('p', {
                    'data-hint': 'Total put premium on executed contracts observed over $2.5k.'})
                if put_premium_element:
                    put_premium = float(put_premium_element.get_text(strip=True).replace('$', '').replace(',', ''))
                else:
                    print("Put premium element not found based on data-hint.")
                    put_premium = 0.0

                if current_signal == "Unknown" and call_premium and put_premium:
                    current_signal = "Bearish" if put_premium > call_premium else "Bullish"

                if prev_signal != current_signal:
                    pro = Process(target=send_msg, args=(current_signal, call_premium, put_premium))
                    pro.start()
                    print(f"Signal change detected. Notification sent: {current_signal}")

                    with open(json_file, "w") as file:
                        json.dump({"prev_signal": current_signal}, file)

                browser.close()

                print(f"Current Signal: {current_signal}")
                print(f"Total Call Premium: ${call_premium}")
                print(f"Total Put Premium: ${put_premium}")

        except Exception as e:
            print(f"An error occurred: {e}")


def run_trend(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    scraper.signal_gen()


def run_alert(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    scraper.notif()


def run_scraper(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    df = scraper.default()
    print(df)


def send_msg(signal, call, put):
    send_message(bot_token=token, user_id=user, signal=signal, call=call, put=put, webhook_url=url, send_to_user=True,
                 send_to_webhook=True)


def driver():
    try:
        df = pd.read_excel("wow.xlsx")

        included_symbols = st.sidebar.multiselect("Include Symbol(s)", options=df['Symbol'].unique(), default=[])
        excluded_symbols = st.sidebar.multiselect("Exclude Symbol(s)", options=df['Symbol'].unique(), default=[])

        if 'custom_spot' not in st.session_state:
            st.session_state.custom_spot = -1.0

        if 'custom_price' not in st.session_state:
            st.session_state.custom_price = -1.0

        if 'custom_premium' not in st.session_state:
            st.session_state.custom_premium = 1.0

        if 'custom_volume' not in st.session_state:
            st.session_state.custom_volume = -1

        if 'custom_size' not in st.session_state:
            st.session_state.custom_size = -1

        if 'filter_date' not in st.session_state:
            st.session_state.filter_date = datetime.today().date()

        if 'filter_time' not in st.session_state:
            st.session_state.filter_time = datetime.now().time()

        if 'call_put_filter' not in st.session_state:
            st.session_state.call_put_filter = "All"

        st.sidebar.write("First select additional filters then press on these buttons")

        if st.sidebar.button("NASDAQ"):
            included_symbols = [
                "AAPL", "AMZN", "MSFT", "FB", "GOOGL", "TSLA", "NFLX", "NVDA", "INTC",
                "CSCO", "PYPL", "ADBE", "CMCSA", "PEP", "AMGN", "COST", "SBUX",
                "TXN", "QCOM", "AVGO", "MDLZ", "NKE", "ISRG", "AMAT", "GILD",
                "ATVI", "FISV", "INTU", "BKNG", "ADP", "CSX", "SNPS", "ZM",
                "MRNA", "BIDU", "FANG", "LRCX", "DOCU", "ILMN", "MAR", "MELI",
                "PDD", "NOW", "EA", "WDAY", "DXCM", "VRSK", "VIV", "NTES"
            ]
            st.session_state.included_symbols = included_symbols

        if st.sidebar.button("US30"):
            included_symbols = [
                "AAPL", "MSFT", "AMZN", "WMT", "JPM", "V", "UNH", "HD", "PG", "JNJ",
                "KO", "CRM", "CVX", "MRK", "CSCO", "MCD", "IBM", "AXP", "CAT", "VZ",
                "DIS", "GS", "AMGN", "HON", "NKE", "BA", "INTC", "MMM", "TRV", "DOW"
            ]
            st.session_state.included_symbols = included_symbols

        st.session_state.call_put_filter = st.sidebar.selectbox("Call/Put", options=["All", "Call", "Put"],
                                                                index=["All", "Call", "Put"].index(st.session_state.call_put_filter))

        st.session_state.custom_spot = st.sidebar.number_input("Spot Limit", min_value=-1.0, max_value=5000.0,
                                                               value=st.session_state.custom_spot, step=0.01)
        st.session_state.custom_price = st.sidebar.number_input("Price Limit", min_value=-1.0, max_value=5000.0,
                                                                value=st.session_state.custom_price, step=0.01)
        st.session_state.custom_premium = st.sidebar.number_input("Premium Limit", min_value=1.0,
                                                                  max_value=999999999999999.0,
                                                                  value=st.session_state.custom_premium, step=0.01)
        st.session_state.custom_volume = st.sidebar.number_input("Volume Limit", min_value=-1,
                                                                 max_value=9999999999,
                                                                 value=st.session_state.custom_volume, step=1)
        st.session_state.custom_size = st.sidebar.number_input("Size Limit", min_value=-1,
                                                               max_value=9999999999,
                                                               value=st.session_state.custom_size, step=1)

        st.session_state.filter_date = st.sidebar.date_input("Filter before date", value=st.session_state.filter_date)
        st.session_state.filter_time = st.sidebar.time_input("Filter before time", value=st.session_state.filter_time)

        if st.sidebar.button("Reset Filters"):
            st.session_state.custom_spot = -1.0
            st.session_state.custom_price = -1.0
            st.session_state.custom_premium = 1.0
            st.session_state.custom_volume = -1
            st.session_state.custom_size = -1
            st.session_state.filter_date = datetime.today().date()
            st.session_state.filter_time = datetime.now().time()
            st.session_state.call_put_filter = "All"
            st.switch_page("pages/filter.py")

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

        if included_symbols:
            filtered_df = df[df['Symbol'].isin(included_symbols)]
        else:
            filtered_df = df[~df['Symbol'].isin(excluded_symbols)]

        filtered_df = filtered_df[filtered_df['Date'] < filter_datetime]
        filtered_df = filtered_df[filtered_df['Spot'] >= st.session_state.custom_spot]
        filtered_df = filtered_df[filtered_df['Price'] >= st.session_state.custom_price]
        filtered_df = filtered_df[filtered_df['Premium'] >= st.session_state.custom_premium]
        filtered_df = filtered_df[filtered_df['Volume'] >= st.session_state.custom_volume]
        filtered_df = filtered_df[filtered_df['Size'] >= st.session_state.custom_size]

        if st.session_state.call_put_filter != "All":
            filtered_df = filtered_df[filtered_df['Call/Put'] == st.session_state.call_put_filter]

        total_call_premium = filtered_df[filtered_df['Call/Put'] == 'Call']['Premium'].sum()
        total_put_premium = filtered_df[filtered_df['Call/Put'] == 'Put']['Premium'].sum()

        if total_call_premium > total_put_premium:
            st.write("Market Sentiment (calculated based on filters): Bearish")
        else:
            st.write("Market Sentiment (calculated based on filters): Bullish")

        st.write(f"Total Call Premium (calculated based on filters): ${total_call_premium:,.2f}")
        st.write(f"Total Put Premium (calculated based on filters): ${total_put_premium:,.2f}")

        filtered_df['Spot'] = filtered_df['Spot'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')
        filtered_df['Price'] = filtered_df['Price'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')
        filtered_df['Premium'] = filtered_df['Premium'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else '--')

        st.dataframe(filtered_df.reset_index(drop=True))

    except Exception as e:
        st.write("No data available")

def main():
    st.title("CapitalFlow Scraper")

    st.session_state['email'] = st.text_input("Enter your email:", value=st.session_state['email'], type="default")
    st.session_state['password'] = st.text_input("Enter your password:", value=st.session_state['password'],
                                                 type="password")

    if st.button("Start Scraping"):
        email = st.session_state['email']
        password = st.session_state['password']

        if email and password:
            queue = Queue()
            process = Process(target=run_scraper, args=(email, password, queue))
            process.start()

            while True:
                if not queue.empty():
                    result = queue.get()

                    if isinstance(result, pd.DataFrame):
                        df = result
                    elif isinstance(result, str) and "error" in result.lower():
                        st.error(result)
                        break
                    else:
                        if st.session_state['signal'] is None:
                            st.session_state['signal'] = result
                        elif st.session_state['call'] is None:
                            st.session_state['call'] = result
                        elif st.session_state['put'] is None:
                            st.session_state['put'] = result

                if not process.is_alive():
                    break

            process.join()

        else:
            st.error("Please provide both email and password.")

    json_file = "signal_call_put_data.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            data = json.load(file)
            st.session_state['signal'] = data.get("signal", "Unknown")
            st.session_state['call'] = data.get("call", "0")
            st.session_state['put'] = data.get("put", "0")
    else:
        st.session_state['signal'] = "Unknown"
        st.session_state['call'] = "0"
        st.session_state['put'] = "0"

    st.write(f"Signal (total taken from website): {st.session_state['signal']}")
    st.write(f"Total Call Premium (total taken from website): ${format(float(st.session_state['call']), ",")}")
    st.write(f"Total Put Premium (total taken from website): ${format(float(st.session_state['put']), ",")}")

def us30_signal(data):
    df = data



def alert():
    if 'run_alert' not in st.session_state:
        st.session_state.run_alert = False

    if st.button("Alerts"):
        st.session_state.run_alert = True

    if st.session_state.run_alert:
        if st.button("Stop Alerts"):
            st.session_state.run_alert = False

    if st.session_state.run_alert:
        email = st.session_state['email']
        password = st.session_state['password']

        if email and password:
            if 'status_message' not in st.session_state:
                st.session_state['status_message'] = "Starting alert checks..."

            status_placeholder = st.empty()

            for i in range(3):
                if not st.session_state.run_alert:
                    break

                st.session_state['status_message'] = f"Running alert check {i + 1}/3..."
                status_placeholder.write(st.session_state['status_message'])

                queue = Queue()
                process = Process(target=run_alert, args=(email, password, queue))
                process.start()

                while True:
                    if not queue.empty():
                        result = queue.get()

                        if isinstance(result, str) and "error" in result.lower():
                            st.error(result)
                            break

                    if not process.is_alive():
                        break

                process.join()

                if i < 2 and st.session_state.run_alert:
                    time.sleep(15 * 60)

        else:
            st.error("Please provide both email and password.")


def trend():
    if 'run_trend' not in st.session_state:
        st.session_state.run_trend = False

    if st.button("Trend"):
        st.session_state.run_trend = True

    if st.session_state.run_trend:
        if st.button("Stop"):
            st.session_state.run_trend = False

    if st.session_state.run_trend:
        email = st.session_state['email']
        password = st.session_state['password']

        if email and password:
            if 'status_msg' not in st.session_state:
                st.session_state['status_msg'] = "Starting alert checks..."

            queue = Queue()
            while st.session_state.run_trend:
                process = Process(target=run_trend, args=(email, password, queue))
                process.start()

                while process.is_alive():
                    if not queue.empty():
                        result = queue.get()
                        if isinstance(result, str) and "error" in result.lower():
                            st.error(result)
                            st.session_state.run_trend = False
                        else:
                            st.write(result)

                process.join()

        else:
            st.error("Please provide both email and password.")


st.title("CapitalFlow Project")
left, right = st.columns(2)

if left.button("Alerts", use_container_width=True):
    st.switch_page("pages/alerts.py")

if right.button("Filters", use_container_width=True):
    st.switch_page("pages/filter.py")
