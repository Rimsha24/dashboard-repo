import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="SuperStore Dashboard", page_icon=":bar_chart:",layout="wide")

# Title
st.title(":bar_chart: SuperStore EDA Dashboard")
st.markdown("<style>div.block-container{padding-top:3rem}</style>", unsafe_allow_html=True)
fl=st.file_uploader(":file_folder: Upload File", type=["csv", "xlsx", "xls","txt"], label_visibility="collapsed")
if fl is not None:
    filename = fl.name
    st.write(f"**File Name:** {filename}")
    df=pd.read_csv(filename, encoding='ISO-8859-1')
else:
    os.chdir(r"D:\COURSES\dataanalysis\task")
    df = pd.read_csv("superstore.csv", encoding='ISO-8859-1')

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
# get min and max date
startdate=pd.to_datetime(df['Order Date'].min(), errors='coerce')
enddate=pd.to_datetime(df['Order Date'].max(), errors='coerce')
with col1:
    date1=pd.to_datetime(st.date_input("Start Date", startdate), errors='coerce')
with col2:
    date2=pd.to_datetime(st.date_input("End Date", enddate), errors='coerce')
df= df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.header("Filter Options")
# create for region
region= st.sidebar.multiselect(
    "Select Region",df['Region'].unique())
if not region:
    df2=df.copy()
else:
    df2 = df[df['Region'].isin(region)]
#create for state
state= st.sidebar.multiselect(
    "Select State",df2['State'].unique())
if not state:           
    df3=df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]
# create for city
city= st.sidebar.multiselect(
    "Select City",df3['City'].unique())
# filter data based on city,region and state
if not region and not state and not city:
    filterdf=df
elif not city and not state:
    filterdf=df[df['Region'].isin(region)]
elif not region and not city:
    filterdf=df[df['State'].isin(state)]
elif state and city:
    filterdf=df3[df3['City'].isin(city) & df3['State'].isin(state)]
elif region and city:
    filterdf=df2[df2['City'].isin(city) & df2['Region'].isin(region)]
elif region and state:
    filterdf=df[df['State'].isin(state) & df['Region'].isin(region)]
elif city:
    filterdf=df3[df3['City'].isin(city)]
else:
    filterdf=df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]
# create a dataframe for category and sales
categorydf = filterdf.groupby(by=['Category'], as_index=False)['Sales'].sum()

# Define columns with equal width (1:1 ratio)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Total Sales by Category")
    fig1 = px.bar(
        categorydf,
        x='Category',
        y='Sales',
        text=[f'${x:,.2f}' for x in categorydf['Sales']],
        template='seaborn',
        color='Sales',
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Total Sales by Category",
        labels={'Sales': 'Total Sales', 'Category': 'Category'}
    )
    fig1.update_layout(height=400)  # set height here
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Region wise Sale")
    fig2 = px.pie(
        filterdf,
        values='Sales',
        names='Region',
        hole=0.5,
        color='Region',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig2.update_traces(text=filterdf["Region"], textposition='outside')
    fig2.update_layout(height=400)  # set height here
    st.plotly_chart(fig2, use_container_width=True)

cl1,cl2=st.columns(2)
with cl1:
    with st.expander("Categorey_viewdata"):
        st.write(categorydf.style.background_gradient(cmap='Blues'))
        csv=categorydf.to_csv( index=False).encode('utf-8')
        st.download_button("Download",data=csv,file_name='category.csv',mime='text/csv'
                           , help="click here to download csv file")
with cl2:
    with st.expander("Region_viewdata"):
        regiondf = filterdf.groupby(by=['Region'], as_index=False)['Sales'].sum()
        st.write(regiondf.style.background_gradient(cmap='Oranges'))
        csv=regiondf.to_csv( index=False).encode('utf-8')
        st.download_button("Download",data=csv,file_name='region.csv',mime='text/csv'
                           , help="click here to download csv file")
        
filterdf["month_year"] = filterdf['Order Date'].dt.to_period('M')

st.subheader("Time series analysis")

linechart = (
    filterdf.groupby(filterdf['month_year'].dt.strftime("%Y-%b"))["Sales"]
    .sum()
    .reset_index()
)

fig2 = px.line(
    linechart,
    x='month_year',
    y='Sales',   # fixed case
    labels={"Sales": "Amount", "month_year": "Month-Year"},
    height=400,
    width=800,
    template='seaborn'  # use a valid template
)

st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data for Time Series Analysis"):
    st.write(linechart.style.background_gradient(cmap='Greens'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download", data=csv, file_name='time_series_analysis.csv', mime='text/csv',
                       help="click here to download csv file")
# create teamap based on region,category, and sub-category
st.subheader("Hierarchical Analysis of sales")
fig3= px.treemap(filterdf, path=['Region', 'Category', 'Sub-Category'], values='Sales',hover_data=['Sales'],
                 color='Sub-Category')
fig3.update_layout(height=600, width=800)
st.plotly_chart(fig3, use_container_width=True)
chart1,chart2=st.columns((2))
with chart1:
    st.subheader("segment wise sales")
    fig=px.pie(filterdf, values='Sales', names='Segment', template='plotly_dark')
    fig.update_traces(text=filterdf["Segment"], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader("Category wise sales")
    fig=px.pie(filterdf, values='Sales', names='Category', template='gridon')
    fig.update_traces(text=filterdf["Category"], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    dfsample=df[0:5][['Region','State','City','Category','Quantity','Sales','Profit']]
    fig=ff.create_table(dfsample,colorscale='Cividis')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-category sales summary")
    filterdf['month'] = filterdf['Order Date'].dt.month_name()
    sub_category_year=pd.pivot_table(data=filterdf,values='Sales',index=['Sub-Category'],columns=['month'])
    st.write(sub_category_year.style.background_gradient(cmap='Purples'))

# Create scatter plot
data1 = px.scatter(filterdf, x='Sales', y='Profit', size='Quantity')

# Correct way to update layout
data1.update_layout(
    title='Sales vs Profit',
    title_font=dict(size=20, color='black'),
    xaxis=dict(title='Sales', title_font=dict(size=19)),
    yaxis=dict(title='Profit', title_font=dict(size=19))
)

st.plotly_chart(data1, use_container_width=True)

# Expander for data view
with st.expander("View Data"):
    st.write(filterdf.iloc[:500, 1:20:2].style.background_gradient(cmap='Reds'))

# Download original dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Original Dataset",
    data=csv,
    file_name='superstore.csv',
    mime='text/csv',
    help="Click here to download original dataset"
)
