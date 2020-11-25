#!/usr/bin/env python3

import yaml
import locale
import requests
from bs4 import BeautifulSoup
import re
import json
from TwitterSearch import *

# Set LC_TIME for datetime
locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


def get_stock_tickers():
    # Get stock tickers for nordic market: large/medium/small cap

    urls = {"large": "http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-large-cap",
            "mid": "http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-mid-cap",
            "small": "http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-small-cap"}

    tickers = {}

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/83.0.4103.97 Safari/537.36"}

    for key, value in urls.items():

        # Get the page
        page = requests.get(value, headers=header)

        # Save it in soup obj
        soup = BeautifulSoup(page.content, "html.parser")

        # Search after class nordic-content, and td tag
        texta = soup.find(attrs={'class': 'nordic-content'}).find_all("td")

        # Create list in dict for each key (large/mid/small cap) to save stock tickers in
        tickers[key] = []

        # Loop through each element
        for string in texta:
            try:
                # Regex search to get the stock tic for each element in the soup object,
                tickers[key].append(re.search('symbol=(.*?)&amp', str(string.renderContents())).group(1))


            except:
                continue

    return tickers


def check_file_exist():
    try:
        f = open("tickers.json")
        return True
    except FileNotFoundError:
        return False

def update_stock_ticker(fresh_tickers):
    with open("tickers.json", "r") as f:
        file_tickers = json.load(f)

        # Compare dicts to see if the stock tick file is equal to the scraped data
        if fresh_tickers == file_tickers:
            f.close()

        # If dicts diffs, update the file
        else:
            f.close()
            save_to_json(fresh_tickers)


def save_to_json(data):
    with open("tickers.json", "w") as f:
        json.dump(data, f)
    f.close()

def get_tweets(tweet_lang, keywords):
    credentials = yaml.safe_load(open("./credentials.yml"))

    try:
        tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
        tso.set_keywords(keywords)  # defines all words that we like to search for in a tweet
        tso.set_language(tweet_lang)  # set the language of tweets we are searching for
        tso.set_include_entities(False)  # no entity information

        # create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key=credentials['consumer_key'],
            consumer_secret=credentials['consumer_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret']
        )

        # Save all tweets in a nested dic
        twitty = {}
        for tweet in ts.search_tweets_iterable(tso):
            # Dict based on tweet ID, assign a new dict as value
            twitty[tweet["id"]] = {}
            # Key is date and value "created at"
            twitty[tweet["id"]]["date"] = tweet["created_at"]
            # Key is text and value is the tweet
            twitty[tweet["id"]]["text"] = tweet["text"]

        return twitty

    except TwitterSearchException as e:
        print(e)


def compare_tweets_to_tickers(tweets):
    with open("tickers.json", "r") as f:
        file_tickers = json.load(f)

        ticker_list = []

        # Convert dict to list
        for i in file_tickers.keys():
            for value in file_tickers[i]:
                ticker_list.append(value)

    stock_tweets = {}
    # Go trough each tweet and compare with stock tickers list
    for key, value in tweets.items():

        for stockticker in ticker_list:

            if stockticker in value["text"]:

                # Check if key already exist if so, append list
                if stockticker in stock_tweets:
                    stock_tweets[stockticker].append(value["text"])

                # Save tweet text as list in stock ticker key
                else:
                    stock_tweets[stockticker] = []
                    stock_tweets[stockticker].append(value["text"])

    return stock_tweets

def main():

    if check_file_exist() is False:
        tickers = get_stock_tickers()
        save_to_json(tickers)

    elif check_file_exist() is True:
        tickers = get_stock_tickers()
        update_stock_ticker(tickers)

    # all entities in the list must exist in the tweet, so only use one at a time
    keyword = ["finanstwitter"]
    tweet_lang = "sv"

    tweets = get_tweets(tweet_lang, keyword)

    stock_tweets = compare_tweets_to_tickers(tweets)

    # Print stock ticker and nr of tweets for each ticker
    for key, value in stock_tweets.items():
        print(key, ":", (len(value)))

# Only run main if executed directly
if __name__ == "__main__":
    main()