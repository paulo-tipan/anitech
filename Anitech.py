import streamlit as st
import pandas as pd

from datetime import datetime

import altair as alt

import psycopg2
from sqlalchemy import create_engine

url = 'postgresql+psycopg2://dashboard_select:AVNS_hf_HkycGlpPX1osvfYX@db-postgresql-sgp1-32435-do-user-12241536-0.b.db.ondigitalocean.com:25060/client_1'
engine = create_engine(url)


# read_data = pd.read_csv('sqss_data.csv')
def query_data_day(start_date_query):
    sql_code = f'''
                SELECT 
                    insert_date,
                    co2x,
                    o2xx,
                    temp,
                    humi,
                    sensor_name
                FROM 
                    sqss_data.location_x
                WHERE DATE(insert_date) = '{start_date_query}'
                ORDER BY insert_date DESC;
                '''
    read_data = pd.read_sql(sql_code,con=engine)
    read_data['insert_date'] = pd.to_datetime(read_data['insert_date'])
    read_data['hour'] = read_data['insert_date'].dt.hour
    dataframe = read_data.groupby(by='hour').mean().reset_index()
    coltorow = dataframe.melt(id_vars=["hour"], 
            var_name="category", 
            value_name="value")
    return coltorow

def plot_data(df, lowerLimit, upperLimit):
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['hour'], empty='none')

    # The basic line
    line = alt.Chart(df).mark_line(interpolate='basis').encode(
        x='hour:Q',
        # y='value:Q',
        y = alt.Y('value:Q', scale=alt.Scale(domain=[lowerLimit, upperLimit])),
        color='category:N'
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x='hour:Q',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'value:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x='hour:Q',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    layer = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=700, height=300
    )
    return (layer).interactive()

def main():
    st.title('AniTech SQSS Data Plot')

    start_date = st.date_input("Date Filter", datetime.today())
    print(start_date)
    st.text("")

    if st.button('Query Data'):
        dataframe = query_data_day(start_date)

        st.text('Temperature in °C and Humidity in %%')
        df_temp = dataframe[dataframe['category'].isin(['temp','humi'])]
        st.altair_chart(plot_data(df_temp,0,100), use_container_width=True)

        st.text('Carbon Dioxide in ppm')
        df_co2x = dataframe[dataframe['category'].isin(['co2x'])]
        st.altair_chart(plot_data(df_co2x,0,2000), use_container_width=True)

        st.text('Oxygen in % vol')
        df_o2xx = dataframe[dataframe['category'].isin(['o2xx'])]
        st.altair_chart(plot_data(df_o2xx,20,25), use_container_width=True)
    else:
        today_date = datetime.today().strftime('%Y-%m-%d')
        dataframe = query_data_day(today_date)

        st.text('Temperature in °C and Humidity in %%')
        df_temp = dataframe[dataframe['category'].isin(['temp','humi'])]
        st.altair_chart(plot_data(df_temp,0,100), use_container_width=True)

        st.text('Carbon Dioxide in ppm')
        df_co2x = dataframe[dataframe['category'].isin(['co2x'])]
        st.altair_chart(plot_data(df_co2x,0,2000), use_container_width=True)

        st.text('Oxygen in % vol')
        df_o2xx = dataframe[dataframe['category'].isin(['o2xx'])]
        st.altair_chart(plot_data(df_o2xx,20,25), use_container_width=True)

if __name__ == "__main__":
    main()