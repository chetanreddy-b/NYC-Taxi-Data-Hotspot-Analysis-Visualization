#!/usr/bin/env python
# coding: utf-8

# ## Load Libraries
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="NYC Taxi Data Analysis",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# pd.set_option("display.max_columns", 30)
# color = sns.color_palette("Paired")
# scale = 'coolwarm_r'

# # ## Load Dataset
# with open(r"data/cleaned/NYC TLC Trip Record - Clean.csv", "r") as file:
#     clean_data = pd.read_csv(file)

# df = clean_data.copy()

# # ## Skimming
# pd.DataFrame(
#     {
#         "feature": df.columns.values,
#         "data_type": df.dtypes.values,
#         "null_value(%)": df.isna().mean().values * 100,
#         "neg_value(%)": [
#             (
#                 len(df[col][df[col] < 0]) / len(df) * 100
#                 if col in df.select_dtypes(include=[np.number]).columns
#                 else 0
#             )
#             for col in df.columns
#         ],
#         "0_value(%)": [
#             (
#                 len(df[col][df[col] == 0]) / len(df) * 100
#                 if col in df.select_dtypes(include=[np.number]).columns
#                 else 0
#             )
#             for col in df.columns
#         ],
#         "duplicate": df.duplicated().sum(),
#         "n_unique": df.nunique().values,
#         "sample_unique": [df[col].unique() for col in df.columns],
#     }
# ).round(3)

# df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
# df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])

# trip_monthly = df.groupby(df['lpep_pickup_datetime'].dt.date).agg(trip_bydate=('lpep_pickup_datetime', 'count')).reset_index()
# trip_monthly['lpep_pickup_datetime'] = pd.to_datetime(trip_monthly['lpep_pickup_datetime'])
# trip_monthly['day_of_week'] = trip_monthly['lpep_pickup_datetime'].dt.day_name()

# trip_dayly = trip_monthly.groupby('day_of_week').agg(trip_byday=('trip_bydate', 'sum'), day_count=('day_of_week', 'count'), avg_trip=('trip_bydate', 'mean')).reset_index()
# trip_dayly['day_cat']= trip_dayly['day_of_week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekdays')

# trip_dayly_cat = trip_dayly.groupby('day_cat').agg(trip_bycat=('trip_byday', 'sum')).reset_index()

# trip_merge = pd.merge(trip_monthly, trip_dayly, on='day_of_week', how='left')
# trip_merge = pd.merge(trip_merge, trip_dayly_cat, on='day_cat', how='left')

# fig1 = plt.figure(figsize=(8, 8))

# plt.suptitle("Trip Distribution based on Day of Week", fontsize=20)
# plt.subplot(2, 1, 1)
# bars = sns.barplot(
#     x=trip_merge["day_of_week"].unique().tolist(),
#     y=trip_merge["avg_trip"].unique().tolist(),
#     palette=color,
# )
# for idx, bar in enumerate(bars.patches):
#     x_value = bar.get_x() + bar.get_width() / 2
#     y_value = bar.get_height() + 20
#     label = "{:.0f}".format(trip_merge["avg_trip"].iloc[idx])
#     plt.text(x_value, y_value, label, ha="center")

# plt.title("Average Trips")
# plt.xlabel("Day of week")
# plt.ylabel("Avg trips")
# plt.yticks(np.arange(0, 2501, 500))

# plt.subplot(2, 1, 2)
# plt.pie(
#     x=trip_merge["trip_byday"].unique().tolist(),
#     labels=trip_merge["day_of_week"].unique().tolist(),
#     pctdistance=0.8,
#     autopct="%1.2f%%",
#     explode=(0, 0, 0.1, 0, 0, 0, 0),
#     colors=color,
# )

# fig = plt.gcf()
# centre_circle = plt.Circle((0, 0), 0.6, fc="white")
# fig.gca().add_artist(centre_circle)
# plt.text(
#     0, 0, trip_merge["trip_byday"].unique().sum(), ha="center", va="center", fontsize=16
# )
# plt.title("Proportion of Total Trips")
# plt.tight_layout()
# plt.savefig("images/fig1.png")
# plt.close()

# day_order = [
#     "Sunday",
#     "Monday",
#     "Tuesday",
#     "Wednesday",
#     "Thursday",
#     "Friday",
#     "Saturday",
# ]
# cross = pd.crosstab(
#     index=df["lpep_pickup_datetime"].dt.day_name(),
#     columns=df["lpep_pickup_datetime"].dt.hour,
#     margins=True,
# ).reindex(day_order)
# cross.columns.name = None
# cross.index.name = "Day of Week"

# melted_cross = (
#     cross.iloc[:, :-1]
#     .reset_index()
#     .melt(id_vars="Day of Week", var_name="hour", value_name="trips")
# )

# unique_days = melted_cross["Day of Week"].unique()
# print("Unique days:", unique_days, "Count:", len(unique_days))

# color = sns.color_palette("coolwarm", len(unique_days))

# fig2 = plt.figure(figsize=(20, 10))

# plt.subplot(2, 1, 1)
# sns.lineplot(data=melted_cross, x="hour", y="trips", hue="Day of Week", palette=color)
# plt.title("Total Trips per Hour", fontsize=14)
# plt.xlabel("Time")
# plt.xticks(np.arange(0, 24, 1))
# plt.ylabel("Total")

# plt.subplot(2, 1, 2)
# sns.heatmap(
#     cross.iloc[:, :-1],
#     cmap="coolwarm",
#     annot=True,
#     fmt="d",
#     cbar_kws={"label": "Number of Trips"},
# )
# plt.title("Total Trips by Day and Hour", fontsize=14)
# plt.xlabel("Hour of the Day")
# plt.ylabel("Day of the Week")

# plt.tight_layout()
# plt.savefig("images/fig2.png")
# plt.close()

# agg_borough = (
#     df.groupby("PUBorough")
#     .agg(count=("PUBorough", "count"))
#     .sort_values(by="count", ascending=False)
#     .reset_index()
# )
# agg_zone = (
#     df.groupby("PUZone")
#     .agg(count=("PUZone", "count"))
#     .sort_values(by="count", ascending=False)
#     .reset_index()
# )

# fig3 = plt.figure(figsize=(15,5))

# plt.subplot(1,2,1)
# bars = sns.barplot(x=agg_borough['PUBorough'],
#                    y=agg_borough['count'],
#                    palette=scale)
# for idx, bar in enumerate(bars.patches):
#     x_value = bar.get_x() + bar.get_width() / 2
#     y_value = bar.get_height() + 200
#     label = "{:.0f}".format(agg_borough['count'].iloc[idx])
#     plt.text(x_value, y_value, label, ha='center')

# plt.title('Trip Distribution based on Pick Up Borough')
# plt.xlabel('Pick Up Borough')
# plt.ylabel('Total trips')

# plt.subplot(1,2,2)
# bars = sns.barplot(data=agg_zone.head(10),
#                    y='PUZone',
#                    x='count',
#                    palette=scale)
# for idx, bar in enumerate(bars.patches):
#     y_value = bar.get_y() + bar.get_height() / 2
#     x_value = bar.get_width() + 400
#     label = "{:.0f}".format(agg_zone['count'].iloc[idx])
#     plt.text(x_value, y_value, label, ha='center')

# plt.title('Trip Distribution based on Pick Up Zone')
# plt.xlabel('Pick Up Zone')
# plt.ylabel('Total trips')

# plt.tight_layout()
# plt.savefig("images/fig3.png")
# plt.close()

# puzone_amount = df.groupby(['DOBorough', 'DOZone']).agg(trip_count=('fare_amount', 'count'),
#                                                         total_fare_amount=('fare_amount', 'sum'),
#                                                         avg_fare_amount=('fare_amount', 'mean'),
#                                                         median_fare_amount=('fare_amount', 'median')
#                                                         ).sort_values(by='total_fare_amount', ascending=False).reset_index().round(2)

# fig = px.treemap(puzone_amount,
#                  path=[px.Constant("All"), 'DOBorough', 'DOZone'],
#                  values='total_fare_amount',
#                  color='median_fare_amount',
#                  color_continuous_scale='RdBu_r',
#                  range_color=[5, 40],
#                  custom_data=['trip_count', 'median_fare_amount'],
#                  title='Heatmap for Average fare amount based on Drop off Location')
# fig.update_traces(hovertemplate='<b>%{label}</b><br>Total Fare: %{value}<br>Trip Count: %{customdata[0]}<br>Median Fare: %{customdata[1]:.2f}')
# fig.update_layout(margin = dict(t=50, l=0, r=0, b=0))
# fig.update_traces(marker=dict(cornerradius=2))
# fig.write_html("images/fig.html")

# trip_data = pd.read_csv("data/train_data/train.csv")

# def fancy_taxi_data(dataframe):

#     dataframe["pickup_year"] = pd.to_datetime(dataframe["pickup_datetime"]).dt.year
#     dataframe["pickup_month"] = pd.to_datetime(dataframe["pickup_datetime"]).dt.month
#     dataframe["pickup_day"] = pd.to_datetime(dataframe["pickup_datetime"]).dt.day
#     dataframe["pickup_time"] = pd.to_datetime(dataframe["pickup_datetime"]).dt.time

#     dataframe["dropoff_year"] = pd.to_datetime(dataframe["dropoff_datetime"]).dt.year
#     dataframe["dropoff_month"] = pd.to_datetime(dataframe["dropoff_datetime"]).dt.month
#     dataframe["dropoff_day"] = pd.to_datetime(dataframe["dropoff_datetime"]).dt.day
#     dataframe["dropoff_time"] = pd.to_datetime(dataframe["dropoff_datetime"]).dt.time

#     dataframe["pickup_day_of_week"] = pd.to_datetime(
#         dataframe["pickup_datetime"]
#     ).dt.day_name()
#     dataframe["dropoff_day_of_week"] = pd.to_datetime(
#         dataframe["dropoff_datetime"]
#     ).dt.day_name()

#     dataframe["is_weekday"] = dataframe["pickup_day_of_week"].apply(
#         lambda x: 0 if x in ["Saturday", "Sunday"] else 1
#     )

#     dataframe["distance_miles"] = (
#         np.sqrt(
#             (dataframe["pickup_latitude"] - dataframe["dropoff_latitude"]) ** 2
#             + (dataframe["pickup_longitude"] - dataframe["dropoff_longitude"]) ** 2
#         )
#         * 69
#     ).round(2)

#     dataframe.drop(["pickup_datetime", "dropoff_datetime"], axis=1, inplace=True)
#     dataframe.drop(["id", "vendor_id", "store_and_fwd_flag"], axis=1, inplace=True)

#     return dataframe

# trip_data = fancy_taxi_data(trip_data)

# def add_daytime_categories(dataframe):
#     daytime_categories = {
#         "middle_of_night": ["00:00:00", "03:59:59"],
#         "early_morning": ["04:00:00", "07:59:59"],
#         "morning": ["08:00:00", "11:59:59"],
#         "afternoon": ["12:00:00", "15:59:59"],
#         "evening": ["16:00:00", "19:59:59"],
#         "night": ["20:00:00", "23:59:59"],
#     }

#     for category, times in daytime_categories.items():
#         daytime_categories[category] = [pd.to_datetime(time).time() for time in times]

#     def daytime_category(time):
#         for category, times in daytime_categories.items():
#             if times[0] <= time <= times[1]:
#                 return category

#     dataframe["pickup_daytime_category"] = dataframe["pickup_time"].apply(
#         daytime_category
#     )
#     dataframe["dropoff_daytime_category"] = dataframe["dropoff_time"].apply(
#         daytime_category
#     )

#     return dataframe

# trip_data["trip_duration_minutes"] = trip_data["trip_duration"].apply(
#     lambda x: round(x / 60, 2)
# )

# trip_data["miles_per_hour"] = trip_data["distance_miles"] / (
#     trip_data["trip_duration_minutes"] / 60
# )

# def remove_outliers_fix_columns(dataframe):
#     dataframe = dataframe[
#         (dataframe["trip_duration_minutes"] < 300)
#         & (dataframe["trip_duration_minutes"] > 1)
#     ]
#     dataframe = dataframe[
#         (dataframe["distance_miles"] < 75) & (dataframe["distance_miles"] > 0.05)
#     ]
#     dataframe = dataframe[
#         (dataframe["miles_per_hour"] < 85) & (dataframe["miles_per_hour"] > 2)
#     ]

#     column_order = [
#         "trip_duration",
#         "trip_duration_minutes",
#         "duration_category",
#         "distance_miles",
#         "miles_per_hour",
#         "is_weekday",
#         "pickup_day_of_week",
#         "pickup_daytime_category",
#         "pickup_year",
#         "pickup_month",
#         "pickup_day",
#         "pickup_time",
#         "dropoff_day_of_week",
#         "dropoff_daytime_category",
#         "dropoff_year",
#         "dropoff_month",
#         "dropoff_day",
#         "dropoff_time",
#         "passenger_count",
#         "pickup_longitude",
#         "pickup_latitude",
#         "dropoff_longitude",
#         "dropoff_latitude",
#     ]
#     dataframe = dataframe.reindex(columns=column_order)

#     dataframe.rename(
#         columns={
#             "trip_duration": "dur_sec",
#             "trip_duration_minutes": "dur_min",
#             "duration_category": "dur_cat",
#             "distance_miles": "dis_mi",
#             "miles_per_hour": "mph",
#             "is_weekday": "is_wkdy",
#             "pickup_day_of_week": "pu_dow",
#             "pickup_daytime_category": "pu_dtc",
#             "pickup_year": "pu_yr",
#             "pickup_month": "pu_mo",
#             "pickup_day": "pu_dy",
#             "pickup_time": "pu_tm",
#             "dropoff_day_of_week": "do_dow",
#             "dropoff_daytime_category": "do_dtc",
#             "dropoff_year": "do_yr",
#             "dropoff_month": "do_mo",
#             "dropoff_day": "do_dy",
#             "dropoff_time": "do_tm",
#             "passenger_count": "pass_cnt",
#             "pickup_longitude": "pu_lon",
#             "pickup_latitude": "pu_lat",
#             "dropoff_longitude": "do_lon",
#             "dropoff_latitude": "do_lat",
#         },
#         inplace=True,
#     )
#     return dataframe

# trip_data = remove_outliers_fix_columns(trip_data)

# routes_sample = trip_data.sample(80)
# routes_sample.to_csv("data/routes_sample.csv", index=False)
routes_sample = pd.read_csv("data/routes_sample.csv")
routes_df = gpd.GeoDataFrame(
    routes_sample,
    geometry=gpd.points_from_xy(routes_sample.pu_lon, routes_sample.pu_lat),
)
fig4 = px.scatter_mapbox(
    routes_df,
    lat="pu_lat",
    lon="pu_lon",
    zoom=12,
    width=800,
    height=450,
    color_continuous_scale=px.colors.cyclical.IceFire,
    mapbox_style="open-street-map",
)
fig4.update_layout(mapbox_style="open-street-map")
fig4.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig4.update_layout(hoverlabel=dict(bgcolor="#444444", font_size=12, font_color="white"))
fig4.add_trace(
    go.Scattermapbox(
        mode="lines",
        lon=routes_df["pu_lon"],
        lat=routes_df["pu_lat"],
        marker={"size": 15},
        line=dict(width=2, color="purple"),
        text=routes_df["pu_lon"],
        opacity=0.5,
        showlegend=False,
        customdata=np.stack(
            (routes_df["dis_mi"], routes_df["dur_min"], routes_df["pu_dtc"]), axis=-1
        ),
    )
)
fig4.update_traces(
    hovertemplate=(
        "<br><b>Distance</b>: %{customdata[0]: .2f} miles<br>"
        + "<br><b>Duration </b>: %{customdata[1]: .2f} min<br>"
        + "<br><b>Time </b>: %{customdata[2]}<br>"
    )
)
col = st.columns((4, 4.5))

with col[0]: 
    st.image("images/fig1.png", use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption(
        "Interactive map showing 80 trips with their duration, distance, and timing patterns"
    )


with col[1]:
    with open("images/fig.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=450)

    st.image("images/fig3.png", use_container_width=True)
    st.image("images/fig2.png", use_container_width=True)
