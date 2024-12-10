# NYC-Taxi-Data-Hotspot-Analysis-Visualization

NYC TAXI DATA ANALYSIS
======================

DESCRIPTION
-----------

Managing NYC's vast taxi network is challenging due to fluctuating demand and inefficiencies in resource allocation. 
This project is a comprehensive analytics solution that processes raw NYC taxi ride data to improve service management. 
The app consists of three main components:

1. Hotspot Prediction: Uses historical data to forecast high-demand pickup locations for effective fleet management
2. Trip Duration Estimation: Implements machine learning models to predict accurate journey times between selected pickup and dropoff locations
3. Time Series Analysis and Forecasting: Analyzes time series data to predict future passenger demand on a particular day

These components work together to provide actionable insights through an interactive dashboard, helping optimize taxi fleet distribution 
and improve service efficiency.

Project Folder Structure:

    data/: Contains raw, cleaned, and processed datasets.
    models/: Stores pre-trained models and encoders.
    notebooks/: Includes Jupyter notebooks for exploratory data analysis and model development.
    pages/: Contains Python scripts for key app functionalities:
        2_Time Series Forecasting.py: Time-series-based daily trip prediction and forecasting.
        3_Taxi Trip Duration Prediction.py: Regression-based trip duration estimation.
        4_Hotspot Analysis.py: Visualization and analysis of pickup/drop-off hotspots.
    images/: Stores output visualizations like plots and maps.
    demo/: Contains the youtube video on how to install and run the app.

INSTALLATION AND EXECUTION
--------------------------
   Installation Steps:
   a) Download the zip file and extract it.

   b) Set Up a Virtual Environment (optional but recommended):
      python -m venv venv
      source venv/bin/activate  # For Linux/Mac
      venv\Scripts\activate     # For Windows

   Go into the code folder and run the below steps
   
   c) Install the requirements:
      pip install -r requirements.txt

   d) Run the Streamlit app:
      streamlit run NYC_Taxi_Data_Analysis.py
      or
      python -m streamlit run NYC_Taxi_Data_Analysis.py

   e) Open the web browser and navigate to the url that appears after starting the app.


DEMO VIDEO
----------
URL: https://youtu.be/0t-izF56qgQ
