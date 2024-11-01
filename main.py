import streamlit as st
from multiprocessing import Process, Queue
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from discord_bot import send_message
import os
import json
import subprocess
from multiprocessing import Process

token = "MTI5ODM4NjAxODA1MDkwMDA2MQ.G_UeMa.hnPypbNGto1XFHni7ZwoEW3B3VWPgcETnJYS_U"
user = "481415673957056518"
url = "https://discord.com/api/webhooks/1299030091636146289/m30T5-SjU_v7K7nZN1Fgs-cylHOB7eUwZ4Y9sbQDOLih43SuNr1crroHqwEoswZLrYy7"

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
                print(self.queue)
                self.queue.put(self.signal)
                print(self.queue.get())
                self.queue.put(self.call)
                self.queue.put(self.put)
                print(self.queue)

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

                self.queue.put(st.session_state['signal'])
                self.queue.put(st.session_state['call'])
                self.queue.put(st.session_state['put'])
                # pro = Process(target=send_msg, args=("xddd", call_premium, put_premium))
                # pro.start()
                # pro.join()
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
                    pro.join()
                browser.close()

                print(f"Current Signal: {current_signal}")
                print(f"Total Call Premium: ${call_premium}")
                print(f"Total Put Premium: ${put_premium}")

        except Exception as e:
            print(f"An error occurred: {e}")


def send_msg(signal, call, put):
    send_message(bot_token=token, user_id=user, signal=signal, call=call, put=put, webhook_url=url, send_to_user=False,
                 send_to_webhook=True)


st.title("CapitalFlow Project")
left, right = st.columns(2)

if left.button("Alerts", use_container_width=True):
    st.switch_page("pages/alerts.py")

if right.button("Filters", use_container_width=True):
    st.switch_page("pages/filter.py")



# st.title("Homepage")
# st.write("Welcome to the Multi-Page Streamlit App!")
# st.sidebar.title("Navigation")
#
# # Automatically generate links to other pages based on Streamlit's multi-page feature
# st.sidebar.markdown("[Go to Filter Page](pages/filter.py)")
# st.sidebar.markdown("[Go to Alert Page](pages/alert.py)")
#
# # You can also add any content you want on the homepage
# st.write("This is the main page. Use the sidebar to navigate to other pages.")