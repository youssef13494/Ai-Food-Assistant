import streamlit as st
import json
import pandas as pd
import altair as alt

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


items = []
for item_name, details in data.items():
    details['item'] = item_name  
    items.append(details)
df = pd.DataFrame(items)
df['color'] = df.apply(
    lambda row: 'red' if row['current_quantity'] <= row['min_quantity'] * 1.1 else 'green',
    axis=1
)

st.write("Inventory Data")

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('item:N', title='المكونات'),
    y=alt.Y('current_quantity:Q', title='الكمية'),
    color=alt.Color('color:N', scale=None)
).properties(
    title='المخزن'
).configure_title(
    anchor='middle',
    fontSize=30 
).configure_axis(
    titleFontSize=20,   
    labelFontSize=16    
)
st.altair_chart(chart, use_container_width=True)
