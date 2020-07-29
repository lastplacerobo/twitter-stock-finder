#!/usr/bin/env python3

import yaml
import locale
import requests
from bs4 import BeautifulSoup
import re

# Set LC_TIME for datetime
locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


def get_stock_tickers():

    # Get stock tickers for nordic market: large/medium/small cap
    # todo: spara i json genom save_to_json, datummärkfilen, hämta ej data om den ej är över 24h gamal

    urls = ["http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-large-cap",
           "http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-mid-cap",
           "http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-small-cap"]

    tickers = []

    for url in urls:

        # Get the page
        page = requests.get(url)

        # Save it in soup obj
        soup = BeautifulSoup(page.content, "html.parser")

        # Search after class nordic-content, and td tag
        texta = soup.find(attrs={'class':'nordic-content'}).find_all("td")
        white = " "
        # Loop through each element
        for a in texta:
            try:
                # Regex search to get the stock tic for each element in the soup object
                tickers.append((re.search('symbol=(.*?)&amp', str(a.renderContents())).group(1)))
            except:
                continue

        # Remove stock tickers trailing A/B/C/D postfix
        i = 0
        for b in tickers:
            tickers[i] = b.split(white, 1)[0]
            i += 1

        # Remove duplicate entries
        tickers = list(dict.fromkeys(tickers))

    return tickers

tickers = get_stock_tickers()




def get_tweets():

    credentials = yaml.safe_load(open("./credentials.yml"))

    """Sök efter hashtag eller trusted users på twitter, spara tweetsen i json fil
    Sök ej på nytt om du sparat tweets med det ID:t eller sökt för den datumperioden redan"""
    """använd save_to_json"""

def save_to_json():
    """Spara input i json struktur med datummärkning"""

def compare_words_to_tickers():
    """Jämför alla ord i tweetsen mot stock tickers"""


def graph_stock_tickers():
    """trenda varje stock tickers för att se vad folk pratar om över tid"""