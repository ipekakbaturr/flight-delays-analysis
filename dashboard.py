import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load data ---
df = pd.read_csv("flight_cleaned.csv")
airport_delay = pd.read_csv("airport_delay_with_coords.csv")
airport_meta = pd.read_csv("airports.csv")
df['ORIGIN_AIRPORT'] = df['ORIGIN_AIRPORT'].astype(str)
airport_meta['IATA_CODE'] = airport_meta['IATA_CODE'].astype(str)

# Merge readable airport names
df = df.merge(
    airport_meta[['IATA_CODE', 'AIRPORT', 'LATITUDE', 'LONGITUDE']],
    how='left',
    left_on='ORIGIN_AIRPORT',
    right_on='IATA_CODE'
)

# Rename for consistency
df = df.rename(columns={"LATITUDE": "LAT", "LONGITUDE": "LON"})

st.set_page_config(layout="wide")
st.title("✈️ US Flight Delays and Cancellations Dashboard")


# --- Sidebar filter ---
st.sidebar.header("Filter by Airport")
airport_options = ['All'] + sorted(df['AIRPORT'].dropna().unique().tolist())
selected_airport = st.sidebar.selectbox("Select Airport", airport_options)

# --- Filter the data ---
filtered_df = df.copy()

if selected_airport != 'All':
    filtered_df = filtered_df[filtered_df['AIRPORT'] == selected_airport]

# --- Show KPIs ---
total_flights = len(filtered_df)
delayed_flights = (filtered_df['DEPARTURE_DELAY'] > 15).sum()

colA, colB = st.columns(2)
with colA:
    st.metric(label="✈️ Total Flights", value=f"{total_flights:,}")
with colB:
    st.metric(label="⏱️ Delayed Flights (>15 min)", value=f"{delayed_flights:,}")

# --- Layout for charts ---
col1, col2 = st.columns(2)

# --- Line Chart: Monthly Delay ---
with col1:
    st.subheader("📈 Avg. Departure Delay by Month")
    monthly = filtered_df.groupby('MONTH')['DEPARTURE_DELAY'].mean().reset_index()
    fig1 = px.line(monthly, x='MONTH', y='DEPARTURE_DELAY', markers=True, height=400)
    st.plotly_chart(fig1, use_container_width=True)

# --- Bar Chart: Delay Reasons ---
with col2:
    st.subheader("📉 Delay Reasons")

    reasons = ['AIR_SYSTEM_DELAY', 'SECURITY_DELAY', 'AIRLINE_DELAY', 'LATE_AIRCRAFT_DELAY', 'WEATHER_DELAY']
    df_reason = filtered_df[reasons].mean().reset_index()
    df_reason.columns = ['Reason', 'Average Delay (min)']

    fig2 = px.bar(df_reason, x='Reason', y='Average Delay (min)', color='Reason', height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("✈️ Delay Distribution")

col3, col4 = st.columns([1, 1])

# GEO MAP (smaller)
with col3:
    st.markdown("**🗺️ Avg. Delay by Airport**")
    filtered_df['ABS_DELAY'] = filtered_df['DEPARTURE_DELAY'].abs()
    map_df = filtered_df.groupby(['ORIGIN_AIRPORT', 'AIRPORT', 'LAT', 'LON'], as_index=False)['DEPARTURE_DELAY'].mean()
    map_df['ABS_DELAY'] = map_df['DEPARTURE_DELAY'].abs()
    map_df = map_df.dropna(subset=['LAT', 'LON', 'ABS_DELAY'])

    fig_map = px.scatter_geo(
        map_df,
        lat='LAT',
        lon='LON',
        size='ABS_DELAY',
        color='DEPARTURE_DELAY',
        color_continuous_scale='RdYlGn_r',
        scope='usa',
        hover_name='AIRPORT',
        height=400
    )
    st.plotly_chart(fig_map, use_container_width=True)

# AVERAGE DELAY PER AIRLINE
with col4:
    st.markdown("**📊 Avg. Delay by Airline**")
    airline_avg = filtered_df.groupby('AIRLINE')['DEPARTURE_DELAY'].mean().reset_index()
    fig_delay = px.bar(airline_avg, x='AIRLINE', y='DEPARTURE_DELAY', color='DEPARTURE_DELAY', height=400)
    st.plotly_chart(fig_delay, use_container_width=True)