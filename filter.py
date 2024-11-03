from func import main, driver
import streamlit as st

if 'email' not in st.session_state:
    st.session_state['email'] = ''
if 'password' not in st.session_state:
    st.session_state['password'] = ''

st.markdown('<a href="http://localhost:8504" target="_blank">Go to HomePage</a>', unsafe_allow_html=True)
main()
driver()