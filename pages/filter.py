import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from main import CapitalFlowScraper
from multiprocessing import Process, Queue


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
                                                                index=["All", "Call", "Put"].index(
                                                                    st.session_state.call_put_filter))

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
        df['Spot'] = df['Spot'].replace({r'\$': '', ',': '', '--': None}, regex=True)
        df['Spot'] = pd.to_numeric(df['Spot'], errors='coerce')
        df['Price'] = df['Price'].replace({r'\$': '', ',': '', '--': None}, regex=True)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Premium'] = df['Premium'].replace({r'\$': '', ',': '', '--': None}, regex=True)
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


def run_scraper(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    df = scraper.default()
    print(df)


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
                    print("queue is not empty")
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


main()
driver()
