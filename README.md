## Implied Volatility Surface Model

An interactive app that displays implied volatility surfaces using real-time option data from the Yahoo Finance API

## How it Works

Given a ticker symbol, the app first fetches the corresponding stock option data via YFinance. Using the Black-Scholes formula for option pricing and Brent's method for efficient root-finding (via SciPy), implied volatility values are backed out of the provided data. SciPy's griddata interpolation function is then used to generate a mesh of values representing a 3D surface, which is then rendered to the user via Plotly.

## Running the Project

To view the deployed app, simply visit:

[https://iadcruz-impliedvolatilitysurface-main-vls3zy.streamlit.app](https://iadcruz-impliedvolatilitysurface-main-vls3zy.streamlit.app)

To run the project locally, ensure you have the required dependencies and run:

```bash
streamlit run main.py
```
