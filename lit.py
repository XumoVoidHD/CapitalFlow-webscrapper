import time
from capital_flow_scraper import CapitalFlowScraper
import pandas as pd
import streamlit as st

st.write("hello")
def say_hello():
    st.write("Hello, Streamlit!")

# Create a button and map it to the function


if __name__ == "__main__":
    email = ''
    password = ''
    if st.button("Click Mwe!"):
        st.write("wow")


    if st.button("Click Me!"):
        scraper = CapitalFlowScraper(email, password)
        scraper.default()
        time.sleep(60)
        df = pd.read_csv("C:\\Users\\vedan\\PycharmProjects\\Web Scrapper\\wow.csv")
        st.write(df)