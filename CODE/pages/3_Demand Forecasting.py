# -*- coding: utf-8 -*-
# pip install streamlit plotly pandas statsmodels

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle
import numpy as np
from datetime import timedelta

# Load deseasonalized data
data = {
    "index": [0, 1, 2, 3, 4, 5, 6],
    "dayofweek": [0, 1, 2, 3, 4, 5, 6],
    "fitted_count": [
        7112.621794871772,
        7691.730769230754,
        7992.826923076907,
        8272.064102564089,
        8495.788461538452,
        8373.846153846152,
        7392.891025641042,
    ],
}
deseason = pd.DataFrame(data)
deseason.set_index("index", inplace=True)

# Load SARIMAX model
try:
    with open("models/sarimax_model_results.pkl", "rb") as file:
        results = pickle.load(file)
except FileNotFoundError:
    st.error(
        "Model file 'sarimax_model_results.pkl' not found. Ensure the file exists in the correct path."
    )
    st.stop()

# Define date ranges
min_date = pd.to_datetime("2016-02-15")
max_date = pd.to_datetime("2026-12-31")

# Streamlit app layout
st.sidebar.header("Interactive Trip Forecasting")

selected_date = st.sidebar.date_input(
    "Select a date for forecasting:", min_date, min_value=min_date, max_value=max_date
)

if selected_date:
    try:
        selected_date = pd.to_datetime(selected_date)
        forecast_steps = 30

        start_date = selected_date - timedelta(days=30)
        end_date = selected_date

        forecast = results.get_forecast(steps=forecast_steps)
        future_dates = pd.date_range(
            start=start_date + timedelta(days=1), periods=forecast_steps
        )
        forecast_values = forecast.predicted_mean

        future_days_of_week = future_dates.dayofweek
        fitted_counts = [
            deseason[deseason["dayofweek"] == day]["fitted_count"].mean()
            + np.random.randint(0, 1000)
            for day in future_days_of_week
        ]
        adjusted_forecast_values = forecast_values + fitted_counts

        forecast_data = pd.DataFrame(
            {"date": future_dates, "forecast": adjusted_forecast_values}
        )
        forecast_data = forecast_data[
            (forecast_data["date"] >= start_date) & (forecast_data["date"] <= end_date)
        ]

        if not forecast_data.empty:
            st.subheader(
                f"Forecasted trips on {selected_date.date()}: {adjusted_forecast_values.iloc[-1]:.2f}"
            )

            # Plot the forecast
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=forecast_data["date"],
                    y=forecast_data["forecast"],
                    mode="lines+markers",
                    name="Forecast",
                    line=dict(color="purple", dash="dash"),
                )
            )
            fig.update_layout(
                title="Time Series of Trips with Forecast (Last 30 Days)",
                xaxis_title="Date",
                yaxis_title="Number of Trips",
                template="plotly_white",
            )
            st.plotly_chart(fig)
        else:
            st.warning("No forecast data available for the selected date range.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
