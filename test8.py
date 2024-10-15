import requests
from bs4 import BeautifulSoup

# Start a session
session = requests.Session()

# Define the login URL and credentials
login_url = 'https://dashboard.capitalflow.app/auth/login'
credentials = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

# Perform the login
response = session.post(login_url, data=credentials)

# Check if login was successful
if response.ok:
    print("Logged in successfully!")
else:
    print("Failed to log in.")

# Access a page that requires login (this is a placeholder, replace with your actual URL)
protected_url = 'https://dashboard.capitalflow.app/'
protected_response = session.get(protected_url)

# Parse the protected page
soup = BeautifulSoup(protected_response.content, features="html.parser")
print(soup.prettify())

# Now, make an XHR request (replace with the actual XHR URL and parameters)
xhr_url = 'https://chdsjvgvuxznwztlpgoe-all.supabase.co/rest/v1/trades_contracts_agg_by_symbol?select=id%2Csymbol%2Cstrike%2Ctype%2Cpremium%2Cupdated%2Cexpiration&day=eq.278&symbol=not.in.%28SPX%2CSPXW%2CRUT%2CNDXP%29&order=premium.desc&limit=20'  # Example XHR URL
headers = {
    'User-Agent': 'Mozilla/5.0',  # Replace with the appropriate headers seen in the browser
    'Accept': 'application/json',
    # Add any other headers (like Authorization if required)
}

# Make the XHR request
xhr_response = session.get(xhr_url, headers=headers)

# Check the response status
if xhr_response.ok:
    print("XHR Data retrieved successfully!")

    # Print the raw response text
    print("Raw response text:", xhr_response.text)

    if 'application/json' in xhr_response.headers.get('Content-Type', ''):
        try:
            data = xhr_response.json()
            print(data)
        except ValueError as e:
            print("Error decoding JSON:", e)
    else:
        print("Response is not in JSON format.")
else:
    print("Failed to retrieve XHR data.")
