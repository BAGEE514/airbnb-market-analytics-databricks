import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from databricks import sql
import os

st.set_page_config(page_title='Airbnb Market Analytics', page_icon='🏠', layout='wide')

@st.cache_resource
def get_conn():
    return sql.connect(
        server_hostname = os.environ['DATABRICKS_HOST'],
        http_path       = os.environ['DATABRICKS_HTTP_PATH'],
        access_token    = os.environ['DATABRICKS_TOKEN'],
    )

@st.cache_data(ttl=3600)
def query(q):
    with get_conn().cursor() as cur:
        cur.execute(q)
        return cur.fetchall_arrow().to_pandas()

df_nbhd   = query('SELECT * FROM workspace.gold.mart_listings_by_neighbourhood')
df_nbhd   = df_nbhd.dropna(subset=['neighbourhood_group'])
df_trends = query('SELECT * FROM workspace.gold.mart_reviews_monthly ORDER BY review_month_start')
df_map    = query('SELECT listing_id, latitude, longitude, price_usd, price_bracket, neighbourhood_group, room_type FROM workspace.airbnb_silver.listings LIMIT 15000')

st.title('🏠 Airbnb Market Analytics — London')
st.caption('Data: Inside Airbnb — Processed with Databricks + dbt')

df_trends = df_trends[pd.to_numeric(df_trends['review_year'], errors='coerce').notna()]
df_trends = df_trends[pd.to_numeric(df_trends['review_month'], errors='coerce').notna()]
df_trends['review_year'] = pd.to_numeric(df_trends['review_year']).astype(int)
df_trends['review_month'] = pd.to_numeric(df_trends['review_month']).astype(int)

st.sidebar.header('🔧 Filters')
sel_nbhds = st.sidebar.multiselect('Neighbourhood Group', sorted(df_nbhd['neighbourhood_group'].unique()), default=sorted(df_nbhd['neighbourhood_group'].unique()))
sel_rooms = st.sidebar.multiselect('Room Type', sorted(df_nbhd['room_type'].unique()), default=sorted(df_nbhd['room_type'].unique()))
yr_min, yr_max = 2015, 2024
sel_years = st.sidebar.slider('Year Range', yr_min, yr_max, (2019, yr_max))

df_n = df_nbhd[df_nbhd['neighbourhood_group'].isin(sel_nbhds) & df_nbhd['room_type'].isin(sel_rooms)]
df_t = df_trends[df_trends['neighbourhood_group'].isin(sel_nbhds) & df_trends['room_type'].isin(sel_rooms) & df_trends['review_year'].between(sel_years[0], sel_years[1])]

c1, c2, c3 = st.columns(3)
c1.metric('Total Listings', f"{df_n['total_listings'].sum():,}")
c2.metric('Unique Hosts', f"{df_n['unique_hosts'].sum():,}")
c3.metric('Avg Nightly Price', f"${df_n['avg_price_usd'].mean():.0f}")
st.divider()

st.subheader('📈 Tile 1 — Market Activity Over Time')
st.caption('Temporal distribution — rubric requirement')
tab1, tab2 = st.tabs(['Review Volume', 'Avg Price Trend'])
with tab1:
    fig = px.line(
        df_t.groupby(['review_month_start', 'neighbourhood_group'])['total_reviews'].sum().reset_index(),
        x='review_month_start', y='total_reviews', color='neighbourhood_group',
        title='Monthly Review Volume by Neighbourhood', template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    fig2 = px.line(
        df_t.groupby(['review_month_start', 'room_type'])['avg_price_usd'].mean().reset_index(),
        x='review_month_start', y='avg_price_usd', color='room_type',
        title='Average Nightly Price Over Time by Room Type', template='plotly_white'
    )
    st.plotly_chart(fig2, use_container_width=True)
st.divider()

st.subheader('📊 Tile 2 — Listings by Neighbourhood Group')
st.caption('Categorical distribution — rubric requirement')
col_a, col_b = st.columns(2)
with col_a:
    fig3 = px.bar(
        df_n.groupby('neighbourhood_group')['total_listings'].sum().reset_index().sort_values('total_listings'),
        x='total_listings', y='neighbourhood_group', orientation='h',
        title='Total Listings by Neighbourhood', template='plotly_white'
    )
    st.plotly_chart(fig3, use_container_width=True)
with col_b:
    fig4 = px.bar(
        df_n.groupby(['neighbourhood_group', 'room_type'])['avg_price_usd'].mean().reset_index(),
        x='neighbourhood_group', y='avg_price_usd', color='room_type', barmode='group',
        title='Avg Nightly Price by Neighbourhood + Room Type', template='plotly_white'
    )
    st.plotly_chart(fig4, use_container_width=True)
st.divider()

st.subheader('🗺️ Bonus — Listing Map by Price Bracket')
COLORS = {
    'Budget (< $75)': '#2ecc71',
    'Mid-range ($75-$150)': '#f39c12',
    'Premium ($150-$300)': '#e74c3c',
    'Luxury ($300+)': '#8e44ad'
}
df_map['latitude'] = pd.to_numeric(df_map['latitude'], errors='coerce')
df_map['longitude'] = pd.to_numeric(df_map['longitude'], errors='coerce')
df_map = df_map.dropna(subset=['latitude', 'longitude'])
m = folium.Map(location=[df_map['latitude'].mean(), df_map['longitude'].mean()], zoom_start=11, tiles='CartoDB positron')
for _, row in df_map.sample(min(3000, len(df_map))).iterrows():
    folium.CircleMarker(
        [row['latitude'], row['longitude']], radius=3,
        color=COLORS.get(row['price_bracket'], '#999'),
        fill=True, fill_opacity=0.7,
        popup=f"{row['neighbourhood_group']} | {row['room_type']} | ${row['price_usd']:.0f}/night"
    ).add_to(m)
st_folium(m, width=1100, height=500)