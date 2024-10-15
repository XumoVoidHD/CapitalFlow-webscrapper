from helium import *
import time

# Define the login URL and credentials
login_url = 'https://dashboard.capitalflow.app/auth/login?nextUrl=/'
credentials = {
    'username': 'adam.marshall8920@gmail.com',
    'password': '@Aa5544163'
}

# Start the Chrome browser in headless mode
browser = start_chrome(login_url, headless=True)

# Log in to the website
write(credentials['username'], into='Email Address')  # Change 'Username' to the actual input field name
write(credentials['password'], into='Password')  # Change 'Password' to the actual input field name
click('Login')  # Change 'Log in' to the actual button text

# Wait for the dashboard page to load
time.sleep(10)  # Adjust 'Dashboard' to something on the protected page

# Now that we're logged in, you can access the protected data
html = browser.page_source

# Print the HTML content of the protected page
print(html)


url = "https://dashboard.capitalflow.app/"
browser = start_chrome(url, headless=True)
html = browser.page_source

print(html)
# Optional: If you want to interact with the data on the protected page, you can do so here

# Close the browser
browser.quit()
