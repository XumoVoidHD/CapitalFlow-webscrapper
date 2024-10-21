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

# Now you can access pages that require login
protected_url = 'https://dashboard.capitalflow.app/'
protected_response = session.get(protected_url)

# Parse the protected page
soup = BeautifulSoup(protected_response.content, features="html.parser")
print(soup.prettify())
