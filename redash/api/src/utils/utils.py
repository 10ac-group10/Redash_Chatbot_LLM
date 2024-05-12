import psycopg2
import os
from langchain_openai import OpenAI
from langchain_core.prompts import SystemMessagePromptTemplate

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

def get_llm_response(question: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")

    # Initialize the OpenAI object
    llm = OpenAI(openai_api_key=api_key)

    # Get the schema of the youtube_data database
    schema = get_schema()

    sql_query_example = "SELECT 'date', 'Content_type_Videos', 'Device type_Mobile phone' FROM youtube_chart_data"

    # Define the system message
    system_message = (f"You are a nice assistant. You are trained to generate SQL queries for Redash based on user's questions. "
                      f"An example is this: {sql_query_example}. But it must note be exact like that. "
                      f"Just note that the table names are enclosed in double quotations and the part after 'FROM'. \n"
                      f"You are not to make up any information, if you don't know, say 'I don't know'. "
                      f"The date field has values in this format: YYYY-MM-DD. "
                      f"You have access to the youtube database with the following schema:\n") + schema

    # Create a SystemMessagePromptTemplate from the system message
    prompt = (
        SystemMessagePromptTemplate.from_template(system_message) + "{question}"
    )

    # Chain the prompt and the OpenAI object together
    llm_chain = prompt | llm

    # Invoke the chain to get a response from the model
    answer = llm_chain.invoke(question)
    answer = filter_llm_answer(answer)
    return answer
