import requests
from bs4 import BeautifulSoup

def scrape_website(url, headers=None):
    response = requests.get(url, headers=None)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text(separator='\n')
    return text