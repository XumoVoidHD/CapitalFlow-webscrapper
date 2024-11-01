import streamlit as st
from main import CapitalFlowScraper
import time
from multiprocessing import Process, Queue
from discord_bot import send_message

if 'email' not in st.session_state:
    st.session_state['email'] = ''
if 'password' not in st.session_state:
    st.session_state['password'] = ''

token = "MTI5ODM4NjAxODA1MDkwMDA2MQ.G_UeMa.hnPypbNGto1XFHni7ZwoEW3B3VWPgcETnJYS_U"
user = "481415673957056518"
url = "https://discord.com/api/webhooks/1299030091636146289/m30T5-SjU_v7K7nZN1Fgs-cylHOB7eUwZ4Y9sbQDOLih43SuNr1crroHqwEoswZLrYy7"


def send_msg(signal, call, put):
    send_message(bot_token=token, user_id=user, signal=signal, call=call, put=put, webhook_url=url, send_to_user=False,
                 send_to_webhook=True)


def run_alert(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    scraper.notif()


def run_trend(email, password, queue):
    scraper = CapitalFlowScraper(email, password, queue)
    scraper.signal_gen()


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
                if not queue.empty():
                    sentiment = queue.get()
                    call_premium = queue.get()
                    put_premium = queue.get()
                    print(f"Retrieved data: {sentiment}, {call_premium}, {put_premium}")
                    pro = Process(target=send_msg, args=(sentiment, call_premium, put_premium))
                    pro.start()
                    print("ran")
                    pro.join()
                else:
                    print("Queue is empty")
                process.join()

                if i < 3 and st.session_state.run_alert:
                    time.sleep(5)


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
                st.session_state['status_msg'] = "Starting trend checks..."

            queue = Queue()
            while st.session_state.run_trend:
                process = Process(target=run_trend, args=(email, password, queue))
                process.start()

                while process.is_alive():
                    if not queue.empty():
                        result = queue.get()
                        print(f"Test 1: {result}")
                        if isinstance(result, str) and "error" in result.lower():
                            st.error(result)
                            st.session_state.run_trend = False
                        else:
                            st.write(result)

                process.join()

        else:
            st.error("Please provide both email and password.")


def run_both():
    if 'run_both' not in st.session_state:
        st.session_state.run_both = False

    if st.button("Run Both"):
        st.session_state.run_both = True

    if st.session_state.run_both:
        if st.button("Stop Both"):
            st.session_state.run_both = False

    if st.session_state.run_both:
        email = st.session_state['email']
        password = st.session_state['password']

        if email and password:
            alert_queue = Queue()
            trend_queue = Queue()

            alert_process = Process(target=run_alert, args=(email, password, alert_queue))
            trend_process = Process(target=run_trend, args=(email, password, trend_queue))

            alert_process.start()
            trend_process.start()

            while st.session_state.run_both:
                if not alert_queue.empty():
                    result = alert_queue.get()
                    if isinstance(result, str) and "error" in result.lower():
                        st.error(result)
                        st.session_state.run_both = False
                    else:
                        st.write(result)

                if not trend_queue.empty():
                    result = trend_queue.get()
                    if isinstance(result, str) and "error" in result.lower():
                        st.error(result)
                        st.session_state.run_both = False
                    else:
                        st.write(result)

                if not alert_process.is_alive() and not trend_process.is_alive():
                    break

            alert_process.join()
            trend_process.join()

        else:
            st.error("Please provide both email and password.")


st.title("Alerts and Trend Page")
st.session_state['email'] = st.text_input("Enter your email:", value=st.session_state['email'], type="default")
st.session_state['password'] = st.text_input("Enter your password:", value=st.session_state['password'],
                                             type="password")
st.write("To get cut and put data every 15min press the 'Alert' button")
alert()
st.write("To get notification when signal changes press the 'Trend' button")
trend()
