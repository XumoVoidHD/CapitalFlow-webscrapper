import streamlit as st

st.title("CapitalFlow Project")
left, right = st.columns(2)

if st.button("Alerts", use_container_width=True):
    # Open alerts page on port 8502
    st.markdown('<a href="http://localhost:8502" target="_blank">Go to Alerts</a>', unsafe_allow_html=True)
    # st.session_state.redirect = "http://localhost:8501"
if st.button("Filters", use_container_width=True):
    # Open filters page on port 8503
    st.markdown('<a href="http://localhost:8501" target="_blank">Go to Filters</a>', unsafe_allow_html=True)
    # st.session_state.redirect = "http://localhost:8502"
if st.button("Trends", use_container_width=True):
    st.markdown('<a href="http://localhost:8503" target="_blank">Go to Trends</a>', unsafe_allow_html=True)

