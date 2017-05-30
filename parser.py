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

    def fetch_page():
        for i in range(3):
            print('Fetching page...')
            browser = webdriver.PhantomJS()
            browser.get(url)
            time.sleep(4)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            browser.close()
            if soup.select('.BookieLogo'):
                return soup

    page = fetch_page()
    if page:
        print('Parsing data...')

        bookies = [b.span.text.strip() for b in page.select('.BookieLogo')]
        if 'Betdaq' in bookies:
            betdaq = bookies.pop()
            bookies = bookies + AHP + [betdaq]
        else:
            bookies = bookies + AHP

        payouts = [p.text.strip() for p in page.select('.Payout')]

        hda = []
        for row in page.select('.OTOddsData')[0].find_all(class_='OTRow'):
            hda.append([clear_string(r.text) for r in row.select('li')])

        print('Done')
        print('Saving data to csv file...')

        with open('{}.csv'.format(filename), 'w') as r:
            writer = csv.writer(r)
            writer.writerow(header)
            result = list(zip_longest(bookies, payouts, hda))
            for row in result:
                writer.writerow([row[0], row[1], row[2][0], row[2][1], row[2][2]])
        print('{} records processed'.format(str(len(result))))
    else:
        print('An error occurred. (Check if link is still alive or try again)')
        return


def parse_asian_or_overunder(url, header, filename):
    """Parse asian-handicap or over-under page. Works for 1st/2nd half also"""

    def fetch_page():
        for i in range(3):
            print('Fetching page...')
            browser = webdriver.PhantomJS()
            browser.get(url)
            time.sleep(4)

            links = browser.find_elements_by_class_name('CollapsibleTitle')
            for l in links:
                l.click()

            soup = BeautifulSoup(browser.page_source, 'lxml')
            browser.close()
            if soup.select('.OutcomeBox'):
                return soup

    page = fetch_page()
    if page:
        print('Parsing data...')

        result = []
        for box in page.select('.OutcomeBox'):
            result.append([box.select('.CollapsibleTitle')[0].text])
            for row in box.find_all('ul', class_='OTRow'):
                result.append([clear_string(r.text.strip()) for r in row.find_all('li', class_='OTCol',
                                                                                  recursive=False)])

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

        print('Done')
        print('Saving data to csv file...')

        with open('{}.csv'.format(filename), 'w') as r:
            writer = csv.writer(r)
            writer.writerow(header)
            for row in result:
                writer.writerow(row)
        print('{} records processed'.format(str(len(result))))
    else:
        print('An error occurred. (Check if link is still alive or try again)')
        return


def main():
    """Run parser depending on the link parameter"""
    link = get_url()
    if 'home-draw-away' in link:
        header = HEADER.get('hda')
        parse_hda(url=link, header=header, filename='hda')
    elif 'asian-handicap' in link:
        header = HEADER.get('asian_or_over')
        parse_asian_or_overunder(url=link, header=header, filename='asian-handicap')
    elif 'over-under' in link:
        header = HEADER.get('asian_or_over')
        parse_asian_or_overunder(url=link, header=header, filename='over-under')
    else:
        print('Please, provide a valid url')


if __name__ == '__main__':
    main()
