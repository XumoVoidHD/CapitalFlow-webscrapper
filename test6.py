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

# After login, access the protected page
dashboard_url = 'https://chdsjvgvuxznwztlpgoe-all.supabase.co/rest/v1/trades_sum_by_type?select=id%2Ccreated%2Ctype%2Ctotal&day=eq.278&agg_type=eq.premium&order=created.desc&limit=2'  # Replace with the correct protected page URL
dashboard_response = session.get(dashboard_url)

# Parse the protected page content
soup = BeautifulSoup(dashboard_response.text, 'html.parser')

# Find all elements with the class "cursor pointer"
elements = soup.find_all(class_="cursor-pointer")

# Iterate through the elements and print the text or desired attribute
for element in elements:
    # Print the text inside the element
    print(element.get_text(strip=True))

    # If you want to extract an attribute (e.g., href or src), use:
    print(element['href'])  # For links
    print(element['src'])  # For images or other media

# Optionally, print the entire HTML structure
print(soup.prettify())
