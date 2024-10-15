import requests
from bs4 import BeautifulSoup
import time
import json


class CapitalFlowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.base_url = 'https://dashboard.capitalflow.app'

    def login(self, username, password):
        login_url = f'{self.base_url}/auth/login'

        # First, get the login page to capture any necessary tokens
        initial_response = self.session.get(login_url, headers=self.headers)

        login_payload = {
            'username': username,
            'password': password
        }

        login_response = self.session.post(
            login_url,
            data=login_payload,
            headers={
                **self.headers,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url
            }
        )

        return login_response.ok

    def get_complete_html(self):
        pages_to_scrape = [
            '',  # Home page
            '/top-contracts',
        ]

        scraped_data = {}

        for page in pages_to_scrape:
            url = f'{self.base_url}{page}'
            try:
                response = self.session.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                scraped_data[page or 'home'] = {
                    'url': url,
                    'html': soup.prettify(),
                    'title': soup.title.string if soup.title else None
                }

                print(f"Successfully scraped {url}")
                time.sleep(2)  # Be respectful with requests

            except requests.RequestException as e:
                print(f"Failed to scrape {url}: {e}")

        return scraped_data

    def save_html_to_files(self, scraped_data):
        for page_name, data in scraped_data.items():
            filename = f'capitalflow_{page_name.strip("/") or "home"}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data['html'])
            print(f"Saved {filename}")

        # Save a JSON index of all pages
        index = {name: {'url': data['url'], 'title': data['title']}
                 for name, data in scraped_data.items()}
        with open('capitalflow_index.json', 'w') as f:
            json.dump(index, f, indent=2)


def main():
    username = 'adam.marshall8920@gmail.com'
    password = '@Aa5544163'

    scraper = CapitalFlowScraper()

    if scraper.login(username, password):
        print("Login successful!")

        scraped_data = scraper.get_complete_html()
        scraper.save_html_to_files(scraped_data)

        print("\nScraping completed!")
        print("Files saved:")
        for page_name in scraped_data.keys():
            print(f"- capitalflow_{page_name.strip('/') or 'home'}.html")
        print("- capitalflow_index.json")
    else:
        print("Login failed. Please check your credentials.")


if __name__ == "__main__":
    main()