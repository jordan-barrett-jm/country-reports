from sqlite3 import paramstyle
import requests
import json
import pandas as pd
import io
import datetime
from concurrent.futures import ThreadPoolExecutor

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
    last_year = datetime.datetime.now().year - 1
    trade_year = last_year
    #this dictionary should be populated with pandas dataframes of exports and imports
    tradeProducts = {
        'exports': pd.DataFrame(),
        'imports': pd.DataFrame()
    }
    numericCode = getNumericCode(countryCode)
    params = {
        'type': 'C',
        'freq':'A',
        'px':'HS',
        'r': numericCode,
        'p': 0,
        'cc': 'AG2',
        'ps': trade_year,
        'fmt': 'csv'
    }
    req_URL = "https://comtrade.un.org/api/get"
    try:
        content_full = False
        while ((trade_year > last_year - 5) and not(content_full)) :
            #get raw CSV data from API endpoint
            urlData = requests.get(req_URL, params=params).content
            #convert data into pandas dataframe
            tradeData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
            if len(tradeData.index) > 1:
                content_full = True
            else:
                trade_year -= 1
                params['ps'] = trade_year
        if content_full:
            #get top commodity imports
            tradeProducts['imports'] = getTopNTradeFlowProducts(tradeData, "Import", 5)
            #get top commodity exports
            tradeProducts['exports'] = getTopNTradeFlowProducts(tradeData, "Export", 5)
    except Exception as e:
        print (e)
    return tradeProducts

def getTopTradePartners(countryCode):
    last_year = datetime.datetime.now().year - 1
    trade_year = last_year
    #this dictionary should be populated with pandas dataframes of exports and imports
    tradePartners = {
        'exports': pd.DataFrame(),
        'imports': pd.DataFrame()
    }
    numericCode = getNumericCode(countryCode)
    params = {
        'type': 'C',
        'freq':'A',
        'px':'HS',
        'r': numericCode,
        'p': 'ALL',
        'cc': 'TOTAL',
        'ps': trade_year,
        'fmt': 'csv'
    }
    req_URL = "https://comtrade.un.org/api/get"
    try:
        content_full = False
        while ((trade_year > last_year - 5) and not(content_full)) :
            #get raw CSV data from API endpoint
            urlData = requests.get(req_URL, params=params).content
            #convert data into pandas dataframe
            tradeData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
            if len(tradeData.index) > 1:
                content_full = True
            else:
                trade_year -= 1
                params['ps'] = trade_year
        if content_full:
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

#multithreaded version of the compareCountry function
def compareCountryParallel(countryCode):
    comp_lst = []
    #These are country codes that denominate regions so they should be excluded from the comparison
    invalid_codes = ['ZH', 'ZI', '1A', 'S3', 
    'B8', 'V2', 'Z4', '4E', 'T4', 'XC', 'Z7',
    '7E', 'T7', 'EU', 'F1', 'XE', 'XD', 'XF',
    'ZT', 'XH', 'XI', 'XG', 'V3', 'ZJ', 'XJ',
    'T2', 'XL', 'XO', 'XM', 'XN', 'ZQ', 'XQ', 
    'T3', 'XP', 'XU', 'OE', 'S4', 'S2', 'V4', 
    'V1', 'S1', '8S', 'T5', 'ZG', 'ZF', 
    'T6', 'XT', '1W']
    def fetchIndicatorCompDetails(indicator):
        last_year = datetime.datetime.now().year - 1
        comp_year = last_year
        indicator_name = indicator['name']
        indicator_code = indicator['WB_name']
        value_filled = False
        while (comp_year >= last_year - 3) and not(value_filled):
            #get the indicator value for all countries
            req_URL = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&date={comp_year}&per_page=300"
            try:
                indicator_data = requests.get(req_URL).json()
                country_dict = next(item for item in indicator_data[1] if item["country"]['id'] == countryCode)
                #check if a valid value is present in the dictionary that contains the country's data
                if country_dict['value']:
                    value_filled = True
                else:
                    comp_year -= 1
            except Exception as e:
                print (e)
                comp_year -= 1
        #if a valid indicator value was found for the specified country
        if value_filled:
            #create an array of dicts with the indicator data in order to create a dataframe
            indicator_arr = [{"Country": x['country']['value'], "Country Code": x['country']['id'],
                             "Year": x['date'], "Indicator Value": x['value']} 
                            for x in indicator_data[1] if (x['value'] is not None 
                            and x['country']['id'] not in invalid_codes)]
            #create indicator df with data from all countries
            indicator_df = pd.DataFrame(indicator_arr)
            indicator_df['Percentile'] = indicator_df['Indicator Value'].rank(method='max', pct=True)
            indicator_df['Rank'] = indicator_df['Indicator Value'].rank(method='max', ascending=False)
            #select the row of the current country
            country_indicator_df = indicator_df[indicator_df["Country Code"] == countryCode]
            country_dict = {
                "Indicator Name": indicator_name, 
                "Indicator Value": country_indicator_df['Indicator Value'].iloc[0],
                "Year": comp_year, 
                "Rank (positional)": country_indicator_df['Rank'].iloc[0], 
                "Percentile": country_indicator_df['Percentile'].iloc[0]
            }
            comp_lst.append(country_dict)     
    indicators = [
        {"name":"Population", "WB_name": "SP.POP.TOTL"},
        {"name":"Urban Population (%)", "WB_name": "SP.URB.TOTL.IN.ZS"},
        {"name":"GDP (US $)", "WB_name": "NY.GDP.MKTP.CD"},
        {"name":"GDP per capita (US $)", "WB_name": "NY.GDP.PCAP.CD"},
        {"name":"Total Exports (US $)", "WB_name": "NE.EXP.GNFS.CD"},
        {"name":"Total Imports (US $)", "WB_name": "NE.IMP.GNFS.CD"},
        {"name":"Trade (% of GDP)", "WB_name": "NE.TRD.GNFS.ZS"},
        {"name":"Land Area (sq. km)", "WB_name": "AG.LND.TOTL.K2"},
        {"name":"Arable Land (% land area)", "WB_name": "AG.LND.ARBL.ZS"},
        {"name":"Arable land (hectares per person)", "WB_name": "AG.LND.ARBL.HA.PC"},
        {"name":"Inflation, consumer prices (annual %)", "WB_name": "FP.CPI.TOTL.ZG"},
        {"name":"Renewable electricity output (% of total)", "WB_name": "EG.ELC.RNEW.ZS"}
    ]
    with ThreadPoolExecutor() as ex:
        for indicator in indicators:
            ex.submit(fetchIndicatorCompDetails, indicator)
    comp_df = pd.DataFrame(comp_lst)
    return comp_df

#parallelised version of the fetchWBIndicatorData function
def fetchWBIndicatorDataParallel(countryCode):
    indicator_data_lst = []
    def getIndicatorData(indicator):
        indicator_code = indicator["WB_name"]
        req_URL = f"https://api.worldbank.org/v2/country/{countryCode}/indicator/{indicator_code}?format=json"
        try:
            res = requests.get(req_URL).json()
            #put data for the last 10 years in a (year, value) tuple
            yearly_data = [(val["date"], val["value"]) for val in res[1]]
            indicator["yearlyData"] = yearly_data
            indicator_data_lst.append(indicator)
        except Exception as e:
            print (e)
    #list of indicators, each of which the yearlyData should be populated
    indicators = [
        {"name":"Population", "WB_name": "SP.POP.TOTL"},
        {"name":"Urban Population (%)", "WB_name": "SP.URB.TOTL.IN.ZS"},
        {"name":"GDP (US $)", "WB_name": "NY.GDP.MKTP.CD"},
        {"name":"GDP per capita (US $)", "WB_name": "NY.GDP.PCAP.CD"},
        {"name":"Total Exports (US $)", "WB_name": "NE.EXP.GNFS.CD"},
        {"name":"Total Imports (US $)", "WB_name": "NE.IMP.GNFS.CD"},
        {"name":"Trade (% of GDP)", "WB_name": "NE.TRD.GNFS.ZS"},
        {"name":"Land Area (sq. km)", "WB_name": "AG.LND.TOTL.K2"},
        {"name":"Arable Land (% land area)", "WB_name": "AG.LND.ARBL.ZS"},
        {"name":"Arable land (hectares per person)", "WB_name": "AG.LND.ARBL.HA.PC"},
        {"name":"Inflation, consumer prices (annual %)", "WB_name": "FP.CPI.TOTL.ZG"},
        {"name":"Renewable electricity output (% of total)", "WB_name": "EG.ELC.RNEW.ZS"}
    ]
    #populate the yearlyData for each indicator
    with ThreadPoolExecutor() as ex:
        for indicator in indicators:
            ex.submit(getIndicatorData, indicator)
    return indicator_data_lst