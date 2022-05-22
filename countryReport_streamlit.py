import streamlit as st
import seaborn as sns
import pandas as pd
from getCountryData import *
import matplotlib.pyplot as plt
import numpy as np

def plotIndicators(indicators):
    for indicator in indicators:
        x = [int(item[0]) for item in indicator['yearlyData'] if item[1]]
        y = [float(item[1]) for item in indicator['yearlyData'] if item[1]]
        fig, ax = plt.subplots()
        plt.bar(x, y)
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.xticks(rotation=50, fontsize=13)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel(indicator['name'], fontsize=14)
        plt.title(indicator['name'], fontsize=16)
        st.pyplot(fig)

def plotTradePartners(tradeData):
    if tradeData['imports'] is not None:
        st.subheader("Import Partners")
        st.write(tradeData['imports'])
        #plot import partners
        st.write("Top 5 import partners")
        x = tradeData['imports']['Partner'].values
        y = tradeData['imports']['Trade Value (US$)'].astype(float).values
        fig, ax = plt.subplots()
        plt.bar(x, y)
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.xticks(rotation=50, fontsize=13)
        plt.ylabel('Imports (US $)', fontsize=14)
        plt.title('Top 5 Import Partners', fontsize=16)
        st.pyplot(fig)
    #plot export partners
    if tradeData['exports'] is not None:
        st.subheader("Export Partners")
        st.write(tradeData['exports'])
        st.write("Top 5 export partners")
        x = tradeData['exports']['Partner'].values
        y = tradeData['exports']['Trade Value (US$)'].astype(float).values
        fig, ax = plt.subplots()
        plt.bar(x, y)
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.xticks(rotation=50, fontsize=13)
        plt.ylabel('Exports (US $)', fontsize=14)
        plt.title('Top 5 Export Partners', fontsize=16)
        st.pyplot(fig)

def plotTradeCommodities(tradeData):
    if tradeData['imports'] is not None:
        st.subheader("Import Commodities")
        st.write(tradeData['imports'])
        #plot import products
        st.write("Top 5 import commodities")
        x = tradeData['imports']['Commodity'].values
        #shorten the commodity descriptions
        x = list(map(lambda item: item[0:20] + '...', x))
        y = tradeData['imports']['Trade Value (US$)'].astype(float).values
        fig, ax = plt.subplots()
        plt.bar(x, y)
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.xticks(rotation=50, fontsize=13)
        plt.ylabel('Imports (US $)', fontsize=14)
        plt.title('Top 5 Import Commodities', fontsize=16)
        st.pyplot(fig)
    #plot export products
    if tradeData['exports'] is not None:
        st.subheader("Export Commodities")
        st.write(tradeData['exports'])
        st.write("Top 5 export commodities")
        x = tradeData['exports']['Commodity'].values
        #shorten the commodity descriptions
        x = list(map(lambda item: item[0:20] + '...', x))
        y = tradeData['exports']['Trade Value (US$)'].astype(float).values
        fig, ax = plt.subplots()
        plt.bar(x, y)
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.xticks(rotation=50, fontsize=13)
        plt.ylabel('Exports (US $)', fontsize=14)
        plt.title('Top 5 Export Commodities', fontsize=16)
        st.pyplot(fig)

def showCountryDetails(country_details):
    country_details = country_details[0]
    st.subheader(country_details['name'])
    st.write(f"Region: {country_details['region']['value']}")
    st.write(f"Income Level: {country_details['incomeLevel']['value']}")
    st.write(f"Latitude: {country_details['latitude']}")
    st.write(f"Longitude: {country_details['longitude']}")
    st.write(f"Capital: {country_details['capitalCity']}")

st.title("Country Report")
#select box for countries
countryList = getCountryCodes()['Country']
selectedCountry = st.selectbox(
     'Select a country to view its economic/geographic report',
     countryList)
countryCode = getTwoLetterCode(selectedCountry)
if st.button("Show Report"):
    country_indicators = fetchWBIndicatorData(countryCode)
    trade_partners = getTopTradePartners(countryCode)
    trade_commodities = getTopTradeProducts(countryCode)
    country_details = fetchWBCountry(countryCode)

    st.header("Country Details")
    showCountryDetails(country_details)
    st.header("Indicator Plots")
    plotIndicators(country_indicators)
    st.header("Trade Data - Top 5 Import and Export Commodities")
    plotTradeCommodities(trade_commodities)
    st.header("Trade Data - Top 5 Import and Export Partners")
    plotTradePartners(trade_partners)