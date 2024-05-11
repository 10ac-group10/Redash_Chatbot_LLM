import pandas as pd
import psycopg2
import os


# fetch data from google drive reusable function
# TODO - make is reusable further by having the entire path as a parameter
def fetch_data(data_folder_name, file_name, clean_data=False, google_colab=False):
    if clean_data:
        final_path = f'{data_folder_name}/clean/{file_name}.csv'
    else:
        final_path = f'{data_folder_name}/{file_name}.csv'

    if google_colab:
        mount_drive()
        # Fetch data from google drive
        df = pd.read_csv(f"/content/drive/My Drive/10Academy/week3/data/{final_path}")
    else:
        # Fetch data from local
        df = pd.read_csv(f"../data/{final_path}")
    return df


# prompt: fetch data from google drive
def mount_drive():
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)


def fetch_chart_data(data_folder_name, clean_data=False):
    return fetch_data(data_folder_name, 'Chart data', clean_data)


def generate_dataframes(value_columns, clean_data=False):
    dataframes = {}
    for name in value_columns.keys():
        dataframes[name] = fetch_chart_data(name, clean_data)
    return dataframes


def save_preprocessed_data(df: pd.DataFrame, file_path: str) -> None:
    # Extract directory from file path
    dir_path = os.path.dirname(file_path)

    # Create the directory if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)


def reshape_data(dataframes, value_columns):
    reshaped_dataframes = {}
    for name, value_column in value_columns.items():
        # Pivot the data
        pivot_df = dataframes[name].pivot(index='Date', columns=name, values=value_column)

        # Reset the index
        pivot_df.reset_index(inplace=True)

        reshaped_dataframes[name] = pivot_df

    return reshaped_dataframes


def save_reshaped_data(reshaped_dataframes, value_columns):
    for name in value_columns.keys():
        # Save the reshaped data to a csv file
        save_preprocessed_data(reshaped_dataframes[name], f'../data/{name}/clean/Chart data.csv')


def preprocess_data(value_columns):
    dataframes = generate_dataframes(value_columns)
    reshaped_dataframes = reshape_data(dataframes, value_columns)
    save_reshaped_data(reshaped_dataframes, value_columns)


# Function to get the schema from the database
# TODO - make it reusable by having the table connection details and table name as parameters
def get_schema():
    # Connect to your database
    conn = psycopg2.connect(database="youtube_data", user="postgres", password="postgres", host="localhost",
                            port="15432")
    cur = conn.cursor()

    # Query the information_schema to get the schema
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'youtube_chart_data'
    """)
    #
    # # Format the schema into a string
    # schema = "We have a database named youtube_data with the following tables:\n"
    # for row in cur.fetchall():
    #     schema += f"- {row[0]}: Contains information about the {row[0]}. Columns: {row[1]} ({row[2]}).\n"
    # Format the schema into a string
    schema = "The database named youtube_data has the following tables:\n"

    # Initialize an empty dictionary to store table information
    tables = {}

    # Fetch all rows and organize them by table
    for row in cur.fetchall():
        table_name, column_name, data_type = row
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append(f"{column_name} ({data_type})")

    # Add table information to the schema string
    for table_name, columns in tables.items():
        schema += f"- {table_name}: Contains information about the {table_name}. Columns: {', '.join(columns)}.\n"

    return schema
