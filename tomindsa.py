# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 23:39:41 2025

@author: elifz
"""

import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

#XML data loading
def parse_healthkit_export(xml_file):
    #parsing xml file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    #extracting walking and running records.
    records = []
    for record in root.findall("Record"):
        if record.attrib.get("type") == "HKQuantityTypeIdentifierDistanceWalkingRunning":
            records.append({
                "sourceName": record.attrib.get("sourceName"),
                "creationDate": record.attrib.get("creationDate"),
                "startDate": record.attrib.get("startDate"),
                "endDate": record.attrib.get("endDate"),
                "value": float(record.attrib.get("value")),
                "unit": record.attrib.get("unit")
            })

    return pd.DataFrame(records)


xml_file_path = 'export.xml'
df = parse_healthkit_export(xml_file_path)

#convert dates into to actual datetime formats for easy processing
df["startDate"] = pd.to_datetime(df["startDate"])
df["endDate"] = pd.to_datetime(df["endDate"])
df["creationDate"] = pd.to_datetime(df["creationDate"])

#adding the duration in minutes column
df["duration_minutes"] = (df["endDate"] - df["startDate"]).dt.total_seconds() / 60
df["date"] = df["startDate"].dt.date

# total distance walked or runned summation
daily_data = df.groupby("date")["value"].sum().reset_index()
daily_data.columns = ["date", "total_distance_km"]

#graph A: Korea Timeframe Data -Feb 2024 to June 2024-
korea_data = daily_data[(daily_data["date"] >= pd.to_datetime("2024-02-24").date()) &
                        (daily_data["date"] <= pd.to_datetime("2024-06-30").date())]
#making the plot pretty and simple
plt.figure(figsize=(10, 6))
plt.plot(korea_data["date"], korea_data["total_distance_km"], marker='o', linestyle='-', color='green', alpha=0.7)
plt.title("Daily Walking Distance: Last Week of February 2024 to June 2024 (Korea Phase)")
plt.xlabel("Date")
plt.ylabel("Distance (km)")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

#2024 data filtering
data_2024 = daily_data[(daily_data["date"] >= pd.to_datetime("2024-01-01").date()) &
                       (daily_data["date"] <= pd.to_datetime("2024-12-31").date())]

#based on the months assigning the seasons
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

# filtering 2024 data
data_2024 = daily_data[(daily_data["date"] >= pd.to_datetime("2024-01-01").date()) &
                       (daily_data["date"] <= pd.to_datetime("2024-12-31").date())].copy()

#adding seasons based on months
data_2024["season"] = pd.to_datetime(data_2024["date"]).dt.month.map(get_season)

#boxplot creation for walking distances per season
plt.figure(figsize=(10, 6))
data_2024.boxplot(column="total_distance_km", by="season", grid=False, showfliers=True, notch=True, patch_artist=True)
plt.title("Walking Distance Distribution by Season (2024)")
plt.suptitle("")  # Remove default 'boxplot grouped by' title
plt.xlabel("Season")
plt.ylabel("Distance (km)")
plt.show()

#graph B: Comparison of my Korea 2024 vs my 2023 Data
data_2023 = daily_data[(daily_data["date"] >= pd.to_datetime("2023-01-01").date()) &
                       (daily_data["date"] <= pd.to_datetime("2023-12-31").date())]

plt.figure(figsize=(10, 6))
plt.plot(korea_data["date"], korea_data["total_distance_km"], marker='o', linestyle='-', label='Korea 2024', alpha=0.7, color='green')
plt.plot(data_2023["date"], data_2023["total_distance_km"], marker='o', linestyle='-', label='2023', alpha=0.7, color='blue')
plt.title("Comparison of Daily Walking Distance (Korea 2024 vs 2023)")
plt.xlabel("Date")
plt.ylabel("Distance (km)")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

#graph C: Weekly Average Walking Distance
df["week"] = df["startDate"].dt.strftime('%Y-%U')
weekly_data = df.groupby("week")["value"].sum().reset_index()
weekly_data["year_week"] = pd.to_datetime(weekly_data["week"] + '-0', format='%Y-%U-%w')

plt.figure(figsize=(10, 6))
plt.plot(weekly_data["year_week"], weekly_data["value"], marker='o', linestyle='-', alpha=0.7)
plt.title("Weekly Walking Distance Trends Over Time")
plt.xlabel("Week")
plt.ylabel("Total Distance (km)")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()