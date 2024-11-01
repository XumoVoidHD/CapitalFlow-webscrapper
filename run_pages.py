import subprocess
import os

def run_streamlit_page(script_name, port):
    # Run a Streamlit page in a separate process with a specific port
    try:
        # Use os.path.abspath to get the full path to the script
        full_path = os.path.abspath(script_name)
        process = subprocess.Popen(
            ["streamlit", "run", full_path, "--server.port", str(port)],
            cwd=os.path.dirname(full_path)
        )
        return process  # Return the process object
    except Exception as e:
        print(f"Error starting {script_name}: {e}")
        return None  # Return None if there's an error

if __name__ == "__main__":
    # List of scripts to run with their corresponding ports
    pages = [
        ("main.py", 8501),         # Main script on port 8501
        ("pages/filter.py", 8502), # Filter page on port 8502
        ("pages/alert.py", 8503)   # Alert page on port 8503
    ]

    processes = []

    for page, port in pages:
        print(f"Starting {page} on port {port}...")
        process = run_streamlit_page(page, port)
        if process is not None:
            processes.append(process)  # Only append if the process was started successfully

    # Optional: Wait for all processes to complete (you can also handle them separately)
    for process in processes:
        process.wait()
