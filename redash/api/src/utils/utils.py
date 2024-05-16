import psycopg2
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import SystemMessagePromptTemplate
import json

load_dotenv()

# Get the values of the Keys from the environment variables or the .env file
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Function to get the schema from the database
# TODO - make it reusable by having the table connection details and table name as parameters
def get_schema():
    # Connect to your database
    conn = psycopg2.connect(database="youtube_data", user="postgres", password="postgres", host="postgres",
                            port="5432")
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

def filter_llm_answer(answer: str) -> str:
    # Find the index of "System:"
    system_index = answer.find("System:")

    # Get everything after "System:"
    sql_statement = answer[system_index + len("System:"):].strip()

    return sql_statement

def get_llm_response(question: str, chatHistory) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")

    # Initialize the OpenAI object
    llm = OpenAI(openai_api_key=api_key)

    # Get the schema of the youtube_data database
    schema = get_schema()

    chatHistory = json.dumps(chatHistory)

    sql_query_example = "SELECT date, content_type_videos, device_type_mobile_phone FROM youtube_data_schema.youtube_chart_data"

    # Define the system message
    system_message = (f"You are a nice assistant. You are trained to generate SQL queries for Redash based on user's questions. "
                      f"An example is this: {sql_query_example}. But the response could differ and may not be exactly like that. "
                      f"Just note that the table names are enclosed in double quotations and the part after 'FROM' if we have the schema name. \n"
                      f"You are not to make up any information, if you don't know, say 'I don't know'. "
                      f"Ensure you only provide a SQL query as a response without any punctutations, just plain SQL statement"
                      f"The date field has values in this format: YYYY-MM-DD. "
                      f"Avoid something like this: SQL Query: SELECT * FROM youtube_data_schema.youtube_chart_data."
                      f"Only start with SELECT statement without adding anything like 'SQL Query:'."
                      f"And DO NOT RETURN and query with punctuation marks irrelevant like ?"
                      f"You will be given a schema with the table names and columns, do not deviate from the schema given and maintain the casing of the column names as provided in the schema."
                      f"Make sure you provide the correct SQL query with the correct format after FROM part like this: 'FROM youtube_data_schema.youtube_chart_data'."
                      f"Only give the first 10 results if the query is a SELECT statement for better visualizations."
                      f"You have access to the youtube database with the following schema:\n") + schema

    # Create a SystemMessagePromptTemplate from the system message
    prompt = (
        SystemMessagePromptTemplate.from_template(system_message) + "{question}"
    )

    # Chain the prompt and the OpenAI object together
    llm_chain = prompt | llm

    # Invoke the chain to get a response from the model
    answer = llm_chain.invoke(question)
    # answer = filter_llm_answer(answer)
    return answer

######################
# CELERY
######################
def process_results(results):
    # The results returned from the Redash API are in the format:
    # {'columns': [{'name': 'column1', 'type': 'type1'}, {'name': 'column2', 'type': 'type2'}], 'rows': [{'column1': 'value1', 'column2': 'value2'}]}
    # We'll transform this into a list of dictionaries for easier processing

    processed_results = []

    for row in results['rows']:
        processed_row = {}
        for column in results['columns']:
            column_name = column['name']
            processed_row[column_name] = row[column_name]
        processed_results.append(processed_row)

    return processed_results


def get_column_names_from_query(query):
    import psycopg2

    # Connect to your database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    # Create a cursor object
    cur = conn.cursor()

    # Execute your query
    cur.execute(query)

    # Get column names
    column_names = [desc[0] for desc in cur.description]

    return column_names


def get_y_axis_columns(query):
    column_names = get_column_names_from_query(query)
    # Assuming column_names is your list of column names
    date_index = column_names.index('date')  # Find the index of 'date'
    x_axis = column_names[date_index]  # Assign 'date' to x-axis

    # Assign the remaining columns to y-axis
    y_axis_column_names = column_names[:date_index] + column_names[date_index + 1:]
    return y_axis_column_names

def get_y_axis(query):
    y_axis_column_names = get_y_axis_columns(query)
    y_axis = []
    for column_name in y_axis_column_names:
        label = column_name.replace('_', ' ')  # Replace underscore with space

        y_axis.append({
            "name": column_name,
            "type": "column",
            "label": label
        })

    return y_axis
