import requests
from bs4 import BeautifulSoup

url = 'https://www.addic7ed.com'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print('Error: Could not retrieve website')
    exit()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all <a> tags with the href attribute starting with 'serie/'
serie_links = soup.find_all('a', href=lambda href: href and href.startswith('serie/'))

# Check if any serie_links were found
if not serie_links:
    print('Error: No serie_links found')
    exit()

# Loop through each serie_link and extract the text content
for link in serie_links:
    print(link.get_text())
