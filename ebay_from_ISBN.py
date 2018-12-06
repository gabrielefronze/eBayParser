import pandas
from lxml import html
import requests
from termcolor import colored
from operator import add
from itertools import compress
import re

def get_ebay_listings(url, row):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    results_cnt = int(round(float(tree.xpath('//div[@class="clt"]//h1[@class="rsHdr"]//span[@class="rcnt"]/text()')[0])))

    totals = list()

    if results_cnt != 0:
        prices = tree.xpath('//ul[@id="ListViewInner"]//li//ul[1]//li[@class="lvprice prc"]//span[@class="bold"]/text()')[1::2]
        prices = [s.replace(',', '.') for s in prices]

        shippings = tree.xpath('//ul[@id="ListViewInner"]//li//ul[1]//li[@class="lvshipping"]//span[@class="ship"]//span[1]/text()')
        shippings = [s.replace('\n', '') for s in shippings]
        shippings = [s.replace('\t', '') for s in shippings]
        shippings = [s.replace('+EUR', '') for s in shippings]
        shippings = [s.replace('spedizione', '') for s in shippings]
        shippings = [s.replace('Spedizione', '') for s in shippings]
        shippings = [s.replace('gratis', '0.00') for s in shippings]
        shippings = [s.replace(' ', '') for s in shippings]
        shippings = [x for x in shippings if x]

        shippings = [s.replace(',', '.') for s in shippings]

        titles = tree.xpath('//ul[@id="ListViewInner"]//li//h3[@class="lvtitle"]//a[@class="vip"]/@title')[:results_cnt]
        titles = [tit.replace("Clicca sul link per accedere ", "") for tit in titles]

        prices = prices[:results_cnt]
        shippings = shippings[:results_cnt]
        titles = titles[:results_cnt]

        mask = [((str(row['ISBN']) in str(title)) or re.search(row['Publisher'], str(title), re.IGNORECASE) or (str(row['Year']) in str(title))) for title in titles]

        prices = list(compress(prices, mask))
        shippings = list(compress(shippings, mask))
        titles = list(compress(titles, mask))

        try:
            totals = list( map(add, list(map(float, shippings)), list(map(float, prices))))
            totals = [round(x, 2) for x in totals]
        except ValueError:
            print(colored("\nConversion error\n",'red',attrs=['bold']))

    return totals

def print_results(index, pandas_df):
    if (pandas_df.loc[index,'price'] > 10 and pandas_df.loc[index,'price'] < 20) :
        print(pandas_df.loc[index]);
    elif pandas_df.loc[index,'price'] == -1. :
        print(colored(pandas_df.loc[index], 'blue'))
    elif pandas_df.loc[index,'price'] == 0 :
        print(colored(pandas_df.loc[index], 'red'))
    elif pandas_df.loc[index,'price'] < 10 :
        print(colored(pandas_df.loc[index], 'green'))
    else:
        print(colored(pandas_df.loc[index], 'yellow'))

def print_results(pandas_df):
    for index, row in pandas_df.iterrows():
        if (pandas_df.loc[index,'price'] > 10 and pandas_df.loc[index,'price'] < 20) :
            print(pandas_df.loc[index]);
        elif pandas_df.loc[index,'price'] == -1. :
            print(colored(pandas_df.loc[index], 'blue'))
        elif pandas_df.loc[index,'price'] == 0 :
            print(colored(pandas_df.loc[index], 'red'))
        elif pandas_df.loc[index,'price'] < 10 :
            print(colored(pandas_df.loc[index], 'green'))
        else:
            print(colored(pandas_df.loc[index], 'yellow'))

def retriever(csv_input_file_name, csv_output_file_name = "ebay_prices.csv"):
    df = pandas.read_csv(csv_input_file_name)
    df['Title'] = df['Title'].str.lstrip('0123456789 ')
    df['Title'] = df['Title'].str.rstrip(' ')
    df['Title'] = df['Title'].str.replace("  "," ")
    df['Author'] = df['Author'].str.replace("  "," ")
    df['Url'] = ("https://www.ebay.it/sch/Libri-e-riviste/267/i.html?_from=R40&LH_BIN=1&LH_PrefLoc=1&_sop=15&_udhi&_nkw=")
    df['price'] = 0.

    for index, row in df.iterrows():
        url = row['Url']+(row['Title'].replace(" ", "+"))+"+"+(row['Author'].replace(" ", "+"))
        totals = get_ebay_listings(url, row);

        if len(totals) == 0:
            url = row['Url']+(row['Title'].replace(" ", "+"))
            totals = get_ebay_listings(url, row);

        df.loc[index,'Url'] = url+" "

        if len(totals) > 0:
            df.loc[index,'price'] = min(totals)
        else:
            df.loc[index,'price'] = -1.

        print_results(index, df)
        
    print(df)
    df.to_csv(csv_output_file_name, sep=',', encoding='utf-8')

if __name__ == "__main__":
    retriever("ISBN.csv")