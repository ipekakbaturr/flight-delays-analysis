import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load data ---
import kagglehub

# Download latest version
path = kagglehub.dataset_download("usdot/flight-delays")

print("Path to dataset files:", path)
df = pd.read_csv(path + "/flights.csv")
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

# --- KPI metrics ---
total_flights = len(filtered_df)
total_delayed = filtered_df['DEPARTURE_DELAY'].gt(15).sum()  # Delay > 15 min
total_cancelled = filtered_df['CANCELLED'].sum()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Total Flights", f"{total_flights:,}")
col_kpi2.metric("Delayed Flights", f"{total_delayed:,}")
col_kpi3.metric("Cancelled Flights", f"{int(total_cancelled):,}")

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
    st.markdown("**🗺️ Avg. Delay & Cancellations by Airport**")

    # Group & aggregate
    geo_df = filtered_df.groupby(['ORIGIN_AIRPORT', 'AIRPORT', 'LAT', 'LON'], as_index=False).agg({
        'DEPARTURE_DELAY': 'mean',
        'CANCELLED': 'sum'
    })
    geo_df['ABS_DELAY'] = geo_df['DEPARTURE_DELAY'].abs()
    geo_df['Marker_Type'] = geo_df['CANCELLED'].apply(lambda x: 'Cancelled' if x > 0 else 'Delayed')

    # Drop NAs
    geo_df = geo_df.dropna(subset=['LAT', 'LON', 'ABS_DELAY'])

    fig_map = px.scatter_geo(
        geo_df,
        lat='LAT',
        lon='LON',
        size='ABS_DELAY',
        color='Marker_Type',
        color_discrete_map={'Cancelled': 'blue', 'Delayed': 'red'},
        scope='usa',
        hover_name='AIRPORT',
        hover_data={'DEPARTURE_DELAY': True, 'CANCELLED': True},
        height=400
    )
    st.plotly_chart(fig_map, use_container_width=True)

# AVERAGE DELAY PER AIRLINE
with col4:
    st.markdown("**📊 Avg. Delay & Cancellations by Airline**")

    airline_df = filtered_df.groupby('AIRLINE').agg({
        'DEPARTURE_DELAY': 'mean',
        'CANCELLED': 'sum'
    }).reset_index()

    # Melt dataframe to long format
    df_melted = airline_df.melt(id_vars='AIRLINE', value_vars=['DEPARTURE_DELAY', 'CANCELLED'],
                                var_name='Metric', value_name='Value')

    # Rename for better display
    df_melted['Metric'] = df_melted['Metric'].map({
        'DEPARTURE_DELAY': 'Avg Delay (min)',
        'CANCELLED': 'Cancellations'
    })

    fig_delay = px.bar(
        df_melted,
        x='AIRLINE',
        y='Value',
        color='Metric',
        barmode='group',
        height=400
    )

    fig_delay.update_layout(
        yaxis_title="Value",
        legend_title="Metric",
        margin=dict(t=20, b=20)
    )

    st.plotly_chart(fig_delay, use_container_width=True)