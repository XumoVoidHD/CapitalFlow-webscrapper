import requests

# Access token and protected URL
access_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6Im5vbUcrTEVtelAzYWFSelMiLCJ0eXAiOiJKV1QifQ"
protected_url = 'https://dashboard.capitalflow.app/'

# Set up the headers with the access token
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Make a GET request to the main protected page
response = requests.get(protected_url, headers=headers)

# Check if the request was successful
if response.ok:
    print("Accessed the protected page successfully!")
    print(response.text)  # Print the main page content
else:
    print(f"Failed to access the page. Status code: {response.status_code}")

# Example XHR Request (Identify the actual XHR URLs from browser's Network tab)
xhr_url = "https://dashboard.capitalflow.app/api/xhr-endpoint"  # Replace with actual XHR endpoint
xhr_response = requests.get(xhr_url, headers=headers)

# Check if the XHR request was successful

print("\n")
if xhr_response.ok:
    # Check if the response is JSON
    if 'application/json' in xhr_response.headers.get('Content-Type', ''):
        print("Loaded XHR data successfully!")
        print(xhr_response.json())  # Assuming the XHR data is in JSON format
    else:
        print("The XHR response is not in JSON format:")
        print(xhr_response.text)  # Print the raw response
else:
    print(f"Failed to load XHR data. Status code: {xhr_response.status_code}")
    print(f"Response content: {xhr_response.text}")
