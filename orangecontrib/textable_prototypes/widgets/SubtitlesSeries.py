"""
Class SubtitlesSeries
Copyright 2022-2023 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package.

Orange3-Textable-Prototypes is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable-Prototypes is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes. If not, see
<http://www.gnu.org/licenses/>.
"""

__version__ = u"0.0.1"
__author__ = "Samantha Allendes, Antoine Vigand, Elijah Green, Thomas Rywalski"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

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
