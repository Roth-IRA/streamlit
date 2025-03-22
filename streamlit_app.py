import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, Carl R.")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df_sales = df.set_index('Order_Date', inplace=False)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df_sales.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")

st.write("### (1) add a drop down for Category (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)")
categories = df["Category"].unique()
category = st.selectbox(
    "Select a category:",
    categories)
st.write("Category selected:", category)

st.write("### (2) add a multi-select for Sub_Category *in the selected Category (1)* (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)")
filtered_data = df[df['Category'] == category]
sub_categories = filtered_data['Sub_Category'].unique()
selected_sub_categories = st.multiselect('Select subcategories:', sub_categories)
st.write('Subcategories selected:', selected_sub_categories)

st.write("### (3) show a line chart of sales for the selected items in (2)")
if selected_sub_categories:
    filtered_data = filtered_data[filtered_data['Sub_Category'].isin(selected_sub_categories)]
    filtered_data['Order_Date'] = filtered_data['Order_Date'].dt.to_period('M').dt.to_timestamp()
    monthly_sales_sub = filtered_data.groupby(['Order_Date', 'Sub_Category'])['Sales'].sum().reset_index()
    monthly_sales_pivot = monthly_sales_sub.pivot(index='Order_Date', columns='Sub_Category', values='Sales')
    monthly_sales_pivot = monthly_sales_pivot.fillna(0)
    st.dataframe(monthly_sales_pivot)
    st.line_chart(monthly_sales_pivot, y_label = "Sales")
else:
    st.write('Please select at least one Sub-Category to view the chart.')
  
st.write("### (4) show three metrics (https://docs.streamlit.io/library/api-reference/data/st.metric) for the selected items in (2): total sales, total profit, and overall profit margin (%)")
st.write("### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)")
if selected_sub_categories:
    filtered_data = filtered_data[filtered_data['Sub_Category'].isin(selected_sub_categories)]
    total_sales = filtered_data['Sales'].sum()
    total_profit = filtered_data['Profit'].sum()
    if total_sales > 0:
        profit_margin = (total_profit / total_sales) * 100
    else:
        profit_margin = 0
    overall_total_sales = df['Sales'].sum()
    overall_total_profit = df['Profit'].sum()
    if overall_total_sales > 0:
        overall_profit_margin = (overall_total_profit / overall_total_sales) * 100
    else:
        overall_profit_margin = 0
    profit_margin_delta = profit_margin - overall_profit_margin
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    st.metric(
        label="Overall Profit Margin",
        value=f"{profit_margin:.2f}%",
        delta=f"{profit_margin_delta:.2f}%"
    )
else:
    st.write('Please select at least one Sub-Category to display metrics.')
