import requests
from bs4 import BeautifulSoup

# URL for the login form
login_url = 'https://dashboard.capitalflow.app/auth/login'

# Create a session to persist cookies and manage authentication state
session = requests.Session()

# Prepare the payload (the form data)
login_payload = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

# Send the POST request to log in
login_response = session.post(login_url, data=login_payload)

# Check if login was successful by inspecting the response
if login_response.ok:
    print("Login successful")
else:
    print("Login failed")

# After login, you can use the session object to make requests to other pages
# Example: Scraping a protected page
dashboard_url = 'https://dashboard.capitalflow.app'  # Replace with an actual protected page
dashboard_response = session.get(dashboard_url)

# Parse the protected page content
soup = BeautifulSoup(dashboard_response.text, 'html.parser')
print(soup.prettify())
