import string
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver


HEADER = ['Provider', 'Payout', 'Home', 'Away']


def clear_string(text):
    return ''.join(s for s in text if s in string.printable)

url = 'https://www.betbrain.com/football/germany/bundesliga/tsv-eintracht-braunschweig-v-vfl-wolfsburg/#/over-under/ordinary-time/'

browser = webdriver.PhantomJS()
browser.get(url)
time.sleep(3)
links = browser.find_elements_by_class_name('CollapsibleTitle')
for link in links:
    link.click()

soup = BeautifulSoup(browser.page_source, 'lxml')
browser.close()

result = []
for box in soup.select('.OutcomeBox'):
    result.append([box.select('.CollapsibleTitle')[0].text])
    for row in box.find_all('ul', class_='OTRow'):
        result.append([clear_string(r.text.strip()) for r in row.find_all('li', class_='OTCol', recursive=False)])


def pretty_result():
    for l in result:
        if '%' in l[0]:
            bookie, payout = l[0][:-3], l[0][-3:]
            l[0] = bookie
            l.insert(1, payout)
        elif ')' in l[0]:
            l.insert(0, None)
            l.insert(0, 'Betdaq')
        else:
            l.insert(1, None)
    return result

result = pretty_result()

with open('over_result.csv', 'w') as r:
    writer = csv.writer(r)
    writer.writerow(HEADER)
    for row in result:
        writer.writerow(row)
