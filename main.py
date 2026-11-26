import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv("dataset/SuperMarket Analysis.csv")

# print(data.head())
# print(data.tail())
# print(data.shape)
# print(data.columns)
# print(data.info())
# print(data.describe())
# print(data.isnull().sum())
# print(data.duplicated().sum())


# Convert Date column into datetime format

data["Date"] = pd.to_datetime(data["Date"])

print(data["Date"].dtype)
print(data["Date"].head())

# ==================================
# BASIC SALES ANALYSIS
# ==================================

total_sales = data["Sales"].sum()

print("Total Sales:", total_sales)