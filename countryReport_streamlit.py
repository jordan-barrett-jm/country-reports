import streamlit as st
import seaborn as sns
import pandas as pd
from getCountryData import *
import matplotlib.pyplot as plt

st.text_input("Enter Country Code eg. JM", key="countryCode")
country_indicators = fetchWBIndicatorData(st.session_state.countryCode)

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
st.write("Indicator Plots")
plotIndicators(country_indicators)