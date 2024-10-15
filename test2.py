import requests

login_url = 'https://capitalflow.app/login'
scrape_url = 'https://capitalflow.app/dashboard'  # The page you want to scrape

# Replace these with your login credentials
login_data = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

# Start a session to persist cookies
session = requests.Session()

# Send a POST request to login
response = session.post(login_url, data=login_data)

# Now you can scrape authenticated pages
scrape_response = session.get(scrape_url)

# Check the content
print(scrape_response.text)
