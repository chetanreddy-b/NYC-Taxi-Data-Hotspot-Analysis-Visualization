import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import folium_static
from datetime import datetime, time
from shapely import wkt
import json

# Configure page settings
st.set_page_config(
    page_title="NYC Taxi Pickups Heatmap",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #ff3333;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    h1 {
        color: #1E1E1E;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_model_and_data():
    model_data = joblib.load('models/decision_tree.pkl')
    model = model_data['model']
    feature_names = model_data['feature_names']
    le = joblib.load('models/locationid_label_encoder.pkl')
    zones_df = pd.read_csv('data/taxi_zones.csv')
    zones_df['geometry'] = zones_df['the_geom'].apply(wkt.loads)
    zones_gdf = gpd.GeoDataFrame(zones_df, geometry='geometry', crs="EPSG:4326")
    return model, feature_names, le, zones_gdf

def predict_pickups(model, feature_names, le, zones_gdf, date, hour):
    input_datetime = datetime.combine(date, time(hour=hour))
    
    zones_gdf = zones_gdf.copy()
    zones_gdf['year'] = input_datetime.year
    zones_gdf['month'] = input_datetime.month
    zones_gdf['day'] = input_datetime.day
    zones_gdf['hour'] = input_datetime.hour
    zones_gdf['day_of_week'] = input_datetime.weekday()
    zones_gdf['weekend'] = (zones_gdf['day_of_week'] >= 5).astype(int)

    features = ['LocationID', 'year', 'month', 'day', 'hour', 'day_of_week', 'weekend']
    X_pred = zones_gdf[features].copy()
    X_pred['LocationID'] = X_pred['LocationID'].apply(
        lambda x: le.transform([x])[0] if x in le.classes_ else -1
    )

    X_pred = X_pred[feature_names]
    y_pred_log = model.predict(X_pred)
    zones_gdf['predicted_pickups'] = np.expm1(y_pred_log)
    return zones_gdf

def generate_map(zones_gdf):
    m = folium.Map(
        location=[40.7128, -74.0060],
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    zones_json = json.loads(zones_gdf.to_json())

    choropleth = folium.Choropleth(
        geo_data=zones_json,
        data=zones_gdf,
        columns=['LocationID', 'predicted_pickups'],
        key_on='feature.properties.LocationID',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Predicted Pickups',
        smooth_factor=0
    ).add_to(m)

    folium.GeoJson(
        zones_json,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 0.5
        },
        tooltip=GeoJsonTooltip(
            fields=['zone', 'predicted_pickups'],
            aliases=['Zone:', 'Predicted Pickups:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """
        )
    ).add_to(m)

    return m

def main():
    with st.sidebar:
        st.markdown("## 🚕 Control Panel")
        st.markdown("---")
        
        current_datetime = datetime.now()
        default_date = current_datetime.date()
        default_hour = current_datetime.hour

        date = st.date_input("📅 Select Date", value=default_date)
        
        hours = [(f"{i:02d}:00") for i in range(24)]
        selected_time = st.selectbox(
            "🕒 Select Hour",
            hours,
            index=default_hour
        )
        selected_hour = int(selected_time.split(':')[0])
        
        st.markdown("---")
        generate_button = st.button("🔄 Generate Heatmap")

    st.title("🗽 NYC Taxi Pickups Heatmap")
    
    model, feature_names, le, zones_gdf = load_model_and_data()

    col1, col2 = st.columns([0.8, 0.2])

    with col1:
        if generate_button:
            with st.spinner("🔄 Generating heatmap..."):
                zones_gdf_pred = predict_pickups(model, feature_names, le, zones_gdf, date, selected_hour)
                m = generate_map(zones_gdf_pred)
                folium_static(m, width=1000, height=700)
        else:
            with st.spinner("📍 Loading default heatmap..."):
                zones_gdf_pred = predict_pickups(model, feature_names, le, zones_gdf, default_date, default_hour)
                m = generate_map(zones_gdf_pred)
                folium_static(m, width=1000, height=700)

    with col2:
        st.markdown("### 📊 Prediction Details")
        st.markdown(f"**Date:** {date}")
        st.markdown(f"**Time Frame:** {selected_time} - {selected_hour:02d}:59")
        st.markdown("*(Predictions are for the full hour)*")
        
        st.markdown("---")
        st.markdown("### 📈 Statistics")
        if 'predicted_pickups' in zones_gdf_pred.columns:
            total_pickups = int(zones_gdf_pred['predicted_pickups'].sum())
            avg_pickups = round(zones_gdf_pred['predicted_pickups'].mean(), 2)
            st.markdown(f"**Total Predicted Pickups:** {total_pickups}")
            st.markdown(f"**Average per Zone:** {avg_pickups}")

if __name__ == "__main__":
    main()