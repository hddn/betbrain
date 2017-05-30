import string
import time
import csv
from itertools import zip_longest

from bs4 import BeautifulSoup
from selenium import webdriver


AHP = ['Average', 'Highest', 'Probability']
HEADER = {
    'hda': ['Bookies', 'Payout', 'Home', 'Draw', 'Away'],
    'asian_or_over': ['Provider', 'Payout', 'Home', 'Away']
}


def get_url():
    """Read url from file"""
    with open('url.txt', 'r') as f:
        data = f.read()
    return data


def clear_string(text):
    """Clear string of not printable characters"""
    return ''.join(s for s in text if s in string.printable)


def parse_hda(url, header, filename):
    """Parse home-draw-away page. Works for 1st/2nd time also"""
    browser = webdriver.PhantomJS()
    browser.get(url)
    time.sleep(4)
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
        hda.append([clear_string(r.text) for r in row.select('li')])

    with open('{}.csv'.format(filename), 'w') as r:
        writer = csv.writer(r)
        writer.writerow(header)
        for row in list(zip_longest(bookies, payouts, hda)):
            writer.writerow([row[0], row[1], row[2][0], row[2][1], row[2][2]])


def parse_asian_or_overunder(url, header, filename):
    """Parse asian-handicap or over-under page. Works for 1st/2nd half also"""
    browser = webdriver.PhantomJS()
    browser.get(url)
    time.sleep(4)
    links = browser.find_elements_by_class_name('CollapsibleTitle')
    for l in links:
        l.click()

    soup = BeautifulSoup(browser.page_source, 'lxml')
    browser.close()

    result = []
    for box in soup.select('.OutcomeBox'):
        result.append([box.select('.CollapsibleTitle')[0].text])
        for row in box.find_all('ul', class_='OTRow'):
            result.append([clear_string(r.text.strip()) for r in row.find_all('li', class_='OTCol', recursive=False)])

    def pretty_result():
        """Split bookies and payouts to different columns"""
        for res in result:
            if '%' in res[0]:
                bookie, payout = res[0][:-3], res[0][-3:]
                if payout == '00%':
                    bookie, payout = res[0][:-4], res[0][-4:]
                res[0] = bookie
                res.insert(1, payout)
            elif ')' in res[0]:
                res.insert(0, None)
                res.insert(0, 'Betdaq')
            else:
                res.insert(1, None)
        return result

    result = pretty_result()

    with open('{}.csv'.format(filename), 'w') as r:
        writer = csv.writer(r)
        writer.writerow(header)
        for row in result:
            writer.writerow(row)


def main():
    """Run parser depending on the link parameter"""
    link = get_url()
    if 'home-draw-away' in link:
        header = HEADER.get('hda')
        parse_hda(url=link, header=header, filename='hda')
    elif 'asian-handicap' in link:
        header = HEADER.get('asian_or_over')
        parse_asian_or_overunder(url=link, header=header, filename='asian-handicap')
    elif 'over-under'in link:
        header = HEADER.get('asian_or_over')
        parse_asian_or_overunder(url=link, header=header, filename='over-under')


if __name__ == '__main__':
    main()
