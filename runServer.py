import subprocess
import sys
import time
import atexit

processes = []


def cleanup():
    for proc in processes:
        proc.terminate()  # Terminate the process
        proc.wait()  # Wait for the process to fully terminate


if __name__ == "__main__":
    # Register the cleanup function to be called on exit
    atexit.register(cleanup)

    # Run each Streamlit app in a separate process
    processes.append(
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "filter.py", "--server.headless", "true"]))
    time.sleep(1)  # Wait for the first app to start
    processes.append(
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "alerts.py", "--server.headless", "true"]))
    time.sleep(1)  # Wait for the first app to start
    processes.append(
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "trends.py", "--server.headless", "true"]))
    time.sleep(1)  # Wait for the second app to start
    processes.append(
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "main.py"]))

    # Optionally, wait for all processes to finish
    for proc in processes:
        proc.wait()  # This will block until the process is terminated
