import string
import time
import csv
from itertools import zip_longest
from bs4 import BeautifulSoup
from selenium import webdriver

AHP = ['Average', 'Highest', 'Probability']
HEADER = ['Bookies', 'Payout', 'Home', 'Draw', 'Away']
url = 'https://www.betbrain.com/football/italy/serie-a/as-roma-v-genoa/#/asian-handicap/ordinary-time/'

browser = webdriver.PhantomJS()
browser.get(url)
time.sleep(3)
links = browser.find_elements_by_class_name('CollapsibleTitle')
for link in links:
    link.click()

soup = BeautifulSoup(browser.page_source, 'lxml')
browser.close()

with open('test.html', 'w') as output_file:
    output_file.write(soup.prettify())


