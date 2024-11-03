from func import alert
import streamlit as st

if 'email' not in st.session_state:
    st.session_state['email'] = ''
if 'password' not in st.session_state:
    st.session_state['password'] = ''

st.markdown('<a href="http://localhost:8504" target="_blank">Go to HomePage</a>', unsafe_allow_html=True)
st.title("Alerts Page")
st.session_state['email'] = st.text_input("Enter your email:", value=st.session_state['email'], type="default")
st.session_state['password'] = st.text_input("Enter your password:", value=st.session_state['password'],
                                             type="password")
st.write("To get cut and put data every 15min press the 'Alert' button")
alert()

