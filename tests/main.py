from bs4 import BeautifulSoup
import requests

url = "https://dashboard.capitalflow.app/auth/login"
res = requests.get(url)

print(BeautifulSoup(res.text, features="html.parser"))