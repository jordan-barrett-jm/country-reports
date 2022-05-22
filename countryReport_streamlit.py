import streamlit as st
import seaborn as sns
import pandas as pd
from getCountryData import *
import matplotlib.pyplot as plt
import numpy as np

st.text_input("Enter Country Code eg. JM", key="countryCode")
country_indicators = fetchWBIndicatorData(st.session_state.countryCode)
trade_partners = getTopTradePartners(st.session_state.countryCode)
trade_commodities = getTopTradeProducts(st.session_state.countryCode)

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


#button to show country codes
if st.button("Show country codes"):
    st.write(getCountryCodes())
st.header("Indicator Plots")
plotIndicators(country_indicators)
st.header("Trade Data - Top 5 Import and Export Commodities")
plotTradeCommodities(trade_commodities)
st.header("Trade Data - Top 5 Import and Export Partners")
plotTradePartners(trade_partners)