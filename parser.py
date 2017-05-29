import string
import time
import csv
from itertools import zip_longest
from bs4 import BeautifulSoup
from selenium import webdriver

AHP = ['Average', 'Highest', 'Probability']
HEADER = ['Bookies', 'Payout', 'Home', 'Draw', 'Away']
url = 'https://www.betbrain.com/football/italy/serie-b/frosinone-v-carpi-fc-1909/#/home-draw-away/ordinary-time/'

browser = webdriver.PhantomJS()
browser.get(url)
time.sleep(3)
soup = BeautifulSoup(browser.page_source, 'lxml')
browser.close()

bookies = [b.span.text.strip() for b in soup.select('.BookieLogo')]

if 'Betdaq' in bookies:
    betdaq = bookies.pop()
    bookies = bookies + AHP + [betdaq]
else:
    bookies = bookies + AHP

payouts = [p.text.strip() for p in soup.select('.Payout')]

hda = []
for row in soup.select('.OTOddsData')[0].find_all(class_='OTRow'):
    hda.append([''.join(s for s in r.text if s in string.printable) for r in row.select('li')])

with open('result.csv', 'w') as r:
    writer = csv.writer(r)
    writer.writerow(HEADER)
    for row in list(zip_longest(bookies, payouts, hda)):
        writer.writerow([row[0], row[1], row[2][0], row[2][1], row[2][2]])
