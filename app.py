import streamlit as st
import pandas as pd

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.sql import text

#url = 'postgresql+psycopg2://username:password@host:port/database'
url = 'postgresql+psycopg2://postgres:1234@localhost:5432/postgres'
engine = create_engine(url)

def main():
    st.title('AniTech SQSS')
    sql_code = '''
        SELECT 
            * 
        FROM 
            client_1.sqss_data
        ORDER BY insert_date DESC;
        '''
    df = pd.read_sql(sql_code,con=engine)

    st.dataframe(df)


if __name__ == "__main__":
    main()