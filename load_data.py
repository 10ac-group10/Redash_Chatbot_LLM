import pandas as pd
from sqlalchemy import create_engine

# Load the data from the CSV file
df = pd.read_csv('./data/youtube_chart_data.csv')

# Create a SQLAlchemy engine
engine = create_engine('postgresql://postgres:postgres@postgres:5432/youtube_data')

# Write the data from the DataFrame to the database
df.to_sql('youtube_chart_data', engine, if_exists='replace', schema='youtube_data_schema', index=False)
