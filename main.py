import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
import datetime
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.interpolate import griddata
import plotly.graph_objects as go

def black_scholes_call_price(sigma, K, S, T, r, q=0):
    d1 = (np.log(S / K) + (r - q + (sigma ** 2) / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def get_implied_vol(price, K, S, T, r, q=0):
    if T <= 0 or price <= 0:
        return np.nan
    try:
        return brentq(lambda sigma: black_scholes_call_price(sigma, K, S, T, r, q) - price, 1e-6, 5)
    except ValueError:
        return np.nan

today = datetime.datetime.today()

st.sidebar.header("Model Configuration")
ticker_symbol = st.sidebar.text_input("Ticker symbol:", value="FAKE").upper()
interest_rate = st.sidebar.number_input("Risk-free Interest Rate:", value=0.015, format="%.4f")
dividend_yield = st.sidebar.number_input('Dividend Yield', value=0.013, format="%.4f")
show_given_implied_vol = st.sidebar.checkbox("Show YFinance implied volatility", value=False)
show_diff = st.sidebar.checkbox("Show volatility diff (Black Scholes - YFinance)", value=False)

with st.spinner("Creating visualization..."):
    try:
        ticker = yf.Ticker(ticker_symbol)
        spot_price = ticker.info["regularMarketPrice"]
    except KeyError:
        st.error("Invalid ticker! Please try again.")
        st.stop()

data_list = []
for expiry in ticker.options:
    if pd.Timestamp(expiry) > today + datetime.timedelta(days=7):
        curr_df = ticker.option_chain(expiry).calls
        curr_df['expiration'] = expiry
        data_list.append(curr_df)

data = pd.concat(data_list)
data = data[(data['bid'] > 0) & (data['ask'] > 0)]
data['time_to_expiry'] = (pd.to_datetime(data['expiration']) - today).dt.days / 365
data['price'] = (data['bid'] + data['ask']) / 2
data['black_scholes_implied_vol'] = data.apply(
    lambda row: get_implied_vol(
        price=row['price'],
        K=row['strike'],
        S=spot_price,
        T=row['time_to_expiry'],
        r=interest_rate,
        q=dividend_yield
    ),
    axis=1
)
data.dropna(inplace=True)
data['vol_diff'] = data['black_scholes_implied_vol'] - data['impliedVolatility']

strikeValues = data['strike'].values
timeValues = data['time_to_expiry'].values

times = np.linspace(timeValues.min(), timeValues.max(), 30)
strikes = np.linspace(strikeValues.min(), strikeValues.max(), 30)
x, y = np.meshgrid(times, strikes)

points = np.column_stack((timeValues, strikeValues))
values = data['vol_diff'].values if show_diff else data['impliedVolatility'].values if show_given_implied_vol else data['black_scholes_implied_vol'].values

z = griddata(points, values, (x, y), method='linear')
z = np.ma.array(z, mask=np.isnan(z))

fig = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='Viridis',)])
fig.update_layout(
    title=dict(text='Black Scholes Implied Volatility Surface'), 
    autosize=False, 
    width=500, 
    height=500, 
    margin=dict(l=65, r=50, b=65, t=90),
    scene=dict(
        xaxis_title="Time to Maturity (Years)",
        yaxis_title="Strike Price",
        zaxis_title="Implied Volatility"
    ),
)

st.plotly_chart(fig, use_container_width=True)