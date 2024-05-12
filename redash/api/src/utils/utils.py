import psycopg2

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
