import logging
import os

import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from quart import Quart, request, jsonify
from redashAPI import RedashAPIClient
from redash_toolbelt import Redash
from utils.chat_history import save_chat_history_redis, get_chat_history_redis
from utils.utils import get_llm_response, get_y_axis

logging.basicConfig(filename='test.log', format='%(filename)s: %(message)s',
                    level=logging.DEBUG)

load_dotenv()

# TODO - Add the Redash API Key to the .env file whenever the user logs in or creates account
# Get the values of the Keys from the environment variables or the .env file
VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")
REDASH_API_KEY = os.environ.get("REDASH_API_KEY")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Define the URL of the Redash instance - In this case, it is the URL of nginx which is the reverse proxy for the Redash server and quart server
REDASH_URL = os.environ.get("REDASH_URL")

# Initialize the Redash object that will be used to interact with the Redash API
redash = Redash(REDASH_URL, REDASH_API_KEY)
RedashApi = RedashAPIClient(REDASH_API_KEY, REDASH_URL)
logging.info(REDASH_API_KEY)

app = Quart(__name__)

# Set the logging level to INFO so that we can see the logs in the console
logging.basicConfig(level=logging.INFO)

# FOR TESTING PURPOSES
query_example = "SELECT content_type_Videos, device_type_mobile_phone, date FROM youtube_data_schema.youtube_chart_data LIMIT 10;"


# Make a simple API request to check if the Redash instance is working
def create_pg_database():
    try:
        data_sources = redash.get_data_sources()
        RedashApi.post('data_sources', {
            "name": "POSTGRES YOUTUBE DATABASE",
            "type": "pg",
            "options": {
                "dbname": "youtube_data",
                "host": "postgres",
                "user": "postgres",
                "passwd": "postgres",
                "port": 5432
            }
        })
        logging.info(data_sources)

    except Exception as e:
        print(e)
        logging.error(e)
        print(f"An error occurred while checking the Redash instance: {e}")


def run() -> None:
    create_pg_database()
    app.run(port=5057)


client = OpenAI(api_key=VARIABLE_KEY)

create_pg_database()


@app.route('/api/chat/echo')
async def echo():
    value = await request.get_json()
    question = value.get('question')
    response_data = {"answer": question}
    return jsonify(response_data), 200


@app.route('/api/chat', methods=['POST'])
async def handle_user_question():
    try:
        value = await request.get_json()
        question = value.get('question')
        chatHistory = value.get('chatHistory')

        # Limit the number of retries
        max_retries = 5
        for attempt in range(max_retries):
            try:
                query = get_llm_response(question, chatHistory)

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

                # If the query is executed successfully, break the loop
                break
            except Exception as error:
                logging.error(error)
                if attempt == max_retries - 1:  # If this was the last attempt
                    return jsonify(
                        {"error": "An error occurred while processing your query. Please try again later."}), 500
                continue

        visualize_results = visualize(query)

        logging.info(visualize_results)

        # ds_id = visualize_results.get('dashboard_id')

        try:

            # Save the chat history to Redis database
            save_chat_history_redis(chatHistory)
            logging.info("WORKS!!!")

            # Retrieve the chat history from Redis
            retrieved_chat_history = get_chat_history_redis()
            logging.info(retrieved_chat_history)

            response_data = {"answer": query, "dashboard_id": "NOT THERE", "chatHistory": retrieved_chat_history}
            return jsonify(response_data), 200

        except Exception as error:
            logging.error(error)

            response_data = {"answer": query, "dashboard_id": "CHAT HISTORY ERROR", "chatHistory": chatHistory}
            return jsonify(response_data), 200

    except Exception as error:
        print(error)
        logging.error(error)
        return jsonify({"answer": query, "dashboard_id": None, "chatHistory": chatHistory}), 200


@app.route('/api/chat/redash/data_sources', methods=['get'])
async def get_queries():
    logging.info(REDASH_API_KEY)
    queries = redash.get_data_sources()
    return jsonify(queries), 200


@app.route('/api/chat/query_results', methods=['post'])
async def get_query_results():
    value = await request.get_json()
    query = value.get('query')

    # query = redash.get_query(query_id)
    # Execute the query and get the results
    results = redash.create_query(query)

    return jsonify(results), 200


@app.route('/api/chat/results', methods=['post'])
async def get_results():
    value = await request.get_json()
    query = value.get('query')
    logging.info(REDASH_API_KEY)
    # Execute the query and get the results
    results = RedashApi.query_and_wait_result(1, query)

    return jsonify(results), 200


@app.route('/api/chat/query', methods=['post'])
async def create_query():
    value = await request.get_json()
    query = value.get('query')
    # Execute the query and get the results
    results = RedashApi.create_query(1, "Mobile Phone views", query)

    data = results.json()

    # Get the data source Id given the data source name
    return jsonify(data), 201


def visualize(query: str):
    y_axis = get_y_axis(query)

    results = RedashApi.create_query(1, "Query 1", query)
    data = results.json()

    query_id = data.get('id')

    logging.info(query_id)

    visualization_results = RedashApi.create_visualization(
        query_id,
        "column",
        "Youtube visualizations",
        x_axis="date",
        y_axis=y_axis
    )

    # Get the visualization id
    viz_id = visualization_results.json().get('id')

    # Create the dashboard for where to add visualizations
    dashboard_results = RedashApi.create_dashboard(
        "Youtube Data Dashboard",
    )

    # Get the dashboard id
    ds_id = dashboard_results.json().get('id')
    logging.info(ds_id)

    # Widget for the visualization
    widget_results = redash.create_widget(
        ds_id,
        viz_id,
        "The youtube views visualization results",
        options={}
    )
    # RedashApi.calculate_widget_position(ds_id, True)

    ids = {
        "query_id": query_id,
        "visualization_id": viz_id,
        "dashboard_id": ds_id,
        # "widget_id": widget_results.json().get('id')
    }

    return ids

# TODO - Add quart schema
# TODO - Perform Testing
