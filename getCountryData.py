from sqlite3 import paramstyle
import requests
import json
import pandas as pd
import io

#this function accepts a country's two-letter ISO code and 
#returns indicator data from the World Bank Indicators API
def fetchWBIndicatorData(countryCode):
    #list of indicators, each of which the yearlyData should be populated
    indicators = [
        {"name":"Population", "WB_name": "SP.POP.TOTL", "yearlyData": []},
        {"name":"Urban Population (%)", "WB_name": "SP.URB.TOTL.IN.ZS", "yearlyData": []},
        {"name":"GDP", "WB_name": "NY.GDP.MKTP.CD", "yearlyData": []},
        {"name":"GDP per capita", "WB_name": "NY.GDP.PCAP.CD", "yearlyData": []},
        {"name":"Total Exports", "WB_name": "NE.EXP.GNFS.CD", "yearlyData": []},
        {"name":"Total Imports", "WB_name": "NE.IMP.GNFS.CD", "yearlyData": []},
        {"name":"Trade (% of GDP)", "WB_name": "NE.TRD.GNFS.ZS", "yearlyData": []},
        {"name":"Land Area (sq. km)", "WB_name": "AG.LND.TOTL.K2", "yearlyData": []},
        {"name":"Arable Land (% land area)", "WB_name": "AG.LND.ARBL.ZS", "yearlyData": []}
    ]
    #populate the yearlyData for each indicator
    for i in range(len(indicators)):
        indicator_code = indicators[i]["WB_name"]
        req_URL = f"https://api.worldbank.org/v2/country/{countryCode}/indicator/{indicator_code}?format=json"
        try:
            res = requests.get(req_URL).json()
            #put data for the last 10 years in a (year, value) tuple
            yearly_data = [(val["date"], val["value"]) for val in res[1][:16]]
            indicators[i]["yearlyData"] = yearly_data
        except Exception as e:
            print (e)
    return indicators

#fetches the Country details using the
#2-letter ISO country code from the WB Country API
def fetchWBCountry(countryCode):
    req_URL  = f"https://api.worldbank.org/v2/country/{countryCode}?format=json"
    try:
        res = requests.get(req_URL).json()
        countryDetails = res[1]
    except Exception as e:
        print (e)
        return {}
    return countryDetails

#get ISO numeric country code from ISO 2-letter country code
def getNumericCode(countryCode):
    codes = pd.read_csv("country_codes.csv")
    try:
        numeric_code = codes[codes['Alpha-2 code'] == countryCode]['Numeric'].values[0]
    except Exception as e:
        print (e)
        return None
    return numeric_code

#Using the UN ComTrade API, retrieve the top products via export and import
#categorized using the 2-digit HS code
#link to documentation on ComTrade API --> https://comtrade.un.org/data/doc/api/#DataRequests
def getTopTradeProducts(countryCode):
    #this dictionary should be populated with pandas dataframes of exports and imports
    tradeProducts = {
        'exports': None,
        'imports': None
    }
    numericCode = getNumericCode(countryCode)
    params = {
        'type': 'C',
        'freq':'A',
        'px':'HS',
        'r': numericCode,
        'p': 0,
        'cc': 'AG2',
        'ps': 2020,
        'fmt': 'csv'
    }
    req_URL = "https://comtrade.un.org/api/get"
    try:
        #get raw CSV data from API endpoint
        urlData = requests.get(req_URL, params=params).content
        #convert data into pandas dataframe
        tradeData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
        #get top commodity imports
        tradeProducts['imports'] = getTopNTradeFlowProducts(tradeData, "Import", 5)
        #get top commodity exports
        tradeProducts['exports'] = getTopNTradeFlowProducts(tradeData, "Export", 5)
    except Exception as e:
        print (e)
    return tradeProducts

def getTopTradePartners(countryCode):
    #this dictionary should be populated with pandas dataframes of exports and imports
    tradePartners = {
        'exports': None,
        'imports': None
    }
    numericCode = getNumericCode(countryCode)
    params = {
        'type': 'C',
        'freq':'A',
        'px':'HS',
        'r': numericCode,
        'p': 'ALL',
        'cc': 'TOTAL',
        'ps': 2020,
        'fmt': 'csv'
    }
    req_URL = "https://comtrade.un.org/api/get"
    try:
        #get raw CSV data from API endpoint
        urlData = requests.get(req_URL, params=params).content
        #convert data into pandas dataframe
        tradeData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
        #get top import partners
        tradePartners['imports'] = getTopNTradeFlowPartners(tradeData, "Import", 5)
        #get top commodity exports
        tradePartners['exports'] = getTopNTradeFlowPartners(tradeData, "Export", 5)
    except Exception as e:
        print (e)
    return tradePartners

def getTopNTradeFlowProducts(tradeDF, tradeFlow, n):
    flow_commodities = tradeDF[tradeDF["Trade Flow"] == tradeFlow]
    top_n_commodities = flow_commodities.nlargest(n, 'Trade Value (US$)')
    return top_n_commodities[["Trade Flow","Year","Classification","Commodity","Trade Value (US$)"]]

def getTopNTradeFlowPartners(tradeDF, tradeFlow, n):
    flow_partners = tradeDF[(tradeDF["Trade Flow"] == tradeFlow) &
                            (tradeDF["Partner"] != "World")]
    top_n_partners = flow_partners.nlargest(n, 'Trade Value (US$)')
    return top_n_partners[["Trade Flow","Year","Partner","Trade Value (US$)"]]

def getCountryCodes():
    codes = pd.read_csv("country_codes.csv")
    return codes[["Country", "Alpha-2 code"]]

def getTwoLetterCode(countryName):
    codes = pd.read_csv("country_codes.csv")
    twoLetterCode = codes[codes["Country"]==countryName]['Alpha-2 code'].values[0]
    return twoLetterCode

getTwoLetterCode("Jamaica")