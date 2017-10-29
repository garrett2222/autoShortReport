from pandas_datareader import data
#import fix_yahoo_finance as yf
import pandas as pd
import urllib2
from bs4 import BeautifulSoup as bs
from datetime import datetime,timedelta
import time
from lxml.html import parse
import numpy as np
import requests


#AVOID GOOGLE FINANCE


###         GET MOST RECENT PRICE           ###
# GOOGLE FINANCE WONT LET ME SCRAPE THIS WELL
"""
def price(ticker):
    while True:
        url = 'http://www.google.com/finance?&q=' + ticker
        res = urllib2.urlopen(url)
        res = res.read()
        soup = bs(res,"lxml")
        si = soup.find("span", {"class": "pr"})
        print si
        try:
            si = si.find_all("span")
        except AttributeError:
            time.sleep(10)
            continue

        stockPrice = si[0].text
        return stockPrice
"""

def get_Exchange(ticker):
    res = requests.get('https://finance.yahoo.com/quote/'+ticker+'?p='+ticker)
    soup = bs(res.content,"lxml")
    exchangeCode = soup.find("div",{"class":'C($c-fuji-grey-j)'})
    exchangeCode = str(exchangeCode.text[0:3].upper())
    return exchangeCode


def get_ADV(ticker):
    res = requests.get('https://finance.yahoo.com/quote/'+ticker+'?p='+ticker)
    soup = bs(res.content,"lxml")
    ADV = soup.find_all("td", {"class":"Ta(end) Fw(b) Lh(14px)"})
    ADV = str(ADV[7])
    startIndex = ADV.find("-->")+3
    endIndex = ADV[startIndex:].find("<!--")
    ADV = ADV[startIndex:endIndex+startIndex]
    ADV = int(ADV.replace(",",""))
    return [ADV]


def get_SI(ticker):
    tree = parse(urllib2.urlopen('https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker))
    shortInterest = tree.xpath("//td[@class='Fz(s) Fw(500) Ta(end)']")
    shortInterest = float(shortInterest[-12].text[:-1])
    return [shortInterest]


###         GET SECTOR         ###
def get_Sector(ticker):
    #MSN VERSION
    exchange = get_Exchange(ticker)
    res = requests.get("https://www.msn.com/en-us/money/stockdetails/company/fi-126.1."+ticker+"."+exchange)
    soup = bs(res.content, "lxml")
    container = soup.find("div", {"class":"caption-sector"})
    child = container.findChildren()
    sector = child[-1].text

    sectors = ["Energy","Basic Materials","Industrials","Consumer Cyclical","Consumer Defensive","Healthcare","Financial Services","Technology","Communications Services","Utilities","Real Estate"]
    sectorsBinary = []
    for item in sectors:
        if item==sector:
            sectorsBinary.append(1)
        else:
            sectorsBinary.append(0)

    """
    Google Finance Version
    <p class="data lastcolumn">Technology</p>
    
    #WARNING!!!! ANY TICKER GOOGLE DOESN'T IMMEDIATE LINK TO AKA SHOPIFY WILL BREAK THIS!!!!
    tree = parse(urllib2.urlopen('http://www.google.com/finance?&q=' + name))
    sector = tree.xpath("//a[@id='sector']")[0].text
    
    sectors = ["Energy","Basic Materials","Industrial","Cyclical Consumer Goods & Services","Non-Cyclical Consumer Goods & Services","Healthcare","Financials","Technology","Telecommunications Services","Utilities","Real Estate"]
    sectorsBinary = []
    for item in sectors:
        if item==sector:
            sectorsBinary.append(1)
        else:
            sectorsBinary.append(0)
    """

    return sectorsBinary


def main(source,ticker):
    ###      GET PRICING INFORMATION      ###
    today = datetime.today()
    todayString = today.strftime('%Y-%m-%d')
    yearago = today - timedelta(days=365)
    yearagoString = yearago.strftime('%Y-%m-%d')

    tickers = [ticker, 'SPY']
    dataSource = 'google'
    start = yearagoString
    end = todayString


    panel_data = data.DataReader(tickers, dataSource, start, end)   #yahoo finance api kinda messed up
    close = panel_data.ix['Close']
    all_weekdays = pd.date_range(start=start, end=end, freq='B')
    close = close.reindex(all_weekdays)
    stockPrices = close[tickers[0]]
    stockPrices = stockPrices[np.isfinite(stockPrices)]
    spyPrices = close[tickers[1]]
    spyPrices = spyPrices[np.isfinite(spyPrices)]

    m3_index = -65
    m1_index = -30

    #DONT HAVE TO WORRY ABOUT 1YR PERFORMACE BEING SHORT FOR IPOS<1YR OLD BECAUSE UNLIKELY DUE TO REGULATION

    stock_1yr_return = (stockPrices[-1] - stockPrices[0]) / stockPrices[0]
    stock_3m_return = (stockPrices[-1] - stockPrices[m3_index]) / stockPrices[m3_index]
    stock_1m_return = (stockPrices[-1] - stockPrices[m1_index]) / stockPrices[m1_index]

    spy_1yr_return = (spyPrices[-1] - spyPrices[0]) / spyPrices[0]
    spy_3m_return = (spyPrices[-1] - spyPrices[m3_index]) / spyPrices[m3_index]
    spy_1m_return = (spyPrices[-1] - spyPrices[m1_index]) / spyPrices[m1_index]

    sourceNames=["Citron","Muddywaters","Prescience","Gotham","Bronte","Sprucepoint","Sirf","NYPost"]
    sourceBinary=[]
    for item in sourceNames:
        if source==item:
            sourceBinary.append(1)
        else:
            sourceBinary.append(0)

    #AGGREGATE DATA
    performance=[spy_1yr_return,spy_3m_return,spy_1m_return,stock_1yr_return,stock_3m_return,stock_1m_return]
    stockADV = get_ADV(ticker)
    shortInterest = get_SI(ticker)
    stockSectors = get_Sector(ticker)

    dataVector=np.concatenate((sourceBinary,performance,shortInterest,stockADV,stockSectors))

    return dataVector



