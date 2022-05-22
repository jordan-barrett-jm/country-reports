import requests
import json
import pandas as pd

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
        {"name":"Population", "WB_name": "SP.POP.TOTL", "yearlyData": []},
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

#fetches the capital of the given country using its
#2-letter ISO country code from the WB Country API
def fetchWBCapital(countryCode):
    req_URL  = f"https://api.worldbank.org/v2/country/{countryCode}?format=json"
    try:
        res = requests.get(req_URL).json()
        capital = res[0]['capitalCity']
    except Exception as e:
        print (e)
    return capital

#get ISO numeric country code from ISO 2-letter country code
def getNumericCode(countryCode):
    codes = pd.read_csv("country_codes.csv")
    try:
        numeric_code = codes[codes['Alpha-2 code'] == countryCode]['Numeric'].values[0]
    except Exception as e:
        print (e)
    return numeric_code

getNumericCode("JM")

