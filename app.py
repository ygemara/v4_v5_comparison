import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to load and preprocess data from multiple files
@st.cache_data
def load_data(files):
    dfs = []
    for file in files:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

# Function to plot v4/v5 for selected sites and country using Plotly
def plot_sites_v4_v5(df, sites, country, main_category=None, sub_category=None):
    # Filter dataframe by country
    country_data = df[df['country'] == country]
    
    # Filter by main_category and sub_category if specified
    if main_category and main_category != 'Unknown':
        country_data = country_data[country_data['main_category'] == main_category]
    if sub_category and sub_category != 'Unknown':
        country_data = country_data[country_data['sub_category'] == sub_category]
    
    # Create figure and axis
    fig = go.Figure()
    
    # Plot data for each site within the specified country using Plotly
    for site in sites:
        site_data = country_data[country_data['domain'] == site]
        fig.add_trace(go.Scatter(x=site_data['date'], y=site_data['v4_v5_ratio'], mode='lines', name=site, text=site))
    
    fig.update_layout(
        title=f'v4/v5 Numbers for Selected Sites in {country} - {main_category if main_category != "Unknown" else ""} - {sub_category if sub_category != "Unknown" else ""}',
        xaxis_title='Date',
        yaxis_title='v4/v5 Values',
        legend_title_text='Sites'
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig)

# Streamlit interface
st.title("v4/v5 Ratio Analysis")

# File upload
uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)
if uploaded_files:
    df = load_data(uploaded_files)
    
    # Display the first few rows of the dataframe
    st.write("Sample data:", df.head())
    
    # Ensure main_category and sub_category columns exist and fill missing values
    if 'main_category' in df.columns:
        df['main_category'].fillna('Unknown', inplace=True)
    else:
        st.write("The 'main_category' column is missing in the uploaded files.")
        df['main_category'] = 'Unknown'
    
    if 'sub_category' in df.columns:
        df['sub_category'].fillna('Unknown', inplace=True)
    else:
        st.write("The 'sub_category' column is missing in the uploaded files.")
        df['sub_category'] = 'Unknown'
        
    # Filter options
    countries = df['country'].unique()
    selected_country = st.selectbox("Select Country", countries)
    
    main_categories = df['main_category'].unique()
    selected_main_category = st.selectbox("Select Main Category", main_categories)
    
    # Dynamically filter sub_categories based on selected main_category
    if selected_main_category != 'Unknown':
        sub_categories = df[df['main_category'] == selected_main_category]['sub_category'].unique()
    else:
        sub_categories = df['sub_category'].unique()
    selected_sub_category = st.selectbox("Select Sub Category", sub_categories)
    
    # Dynamically filter sites based on selected country, main_category, and sub_category
    filtered_df = df[df['country'] == selected_country]
    if selected_main_category != 'Unknown':
        filtered_df = filtered_df[filtered_df['main_category'] == selected_main_category]
    if selected_sub_category != 'Unknown':
        filtered_df = filtered_df[filtered_df['sub_category'] == selected_sub_category]
    
    sites = filtered_df['domain'].unique()
    selected_sites = st.multiselect("Select Sites", sites)
    
    # Plot data
    if st.button("Plot Data"):
        plot_sites_v4_v5(df, selected_sites, selected_country, selected_main_category, selected_sub_category)
