from quart import Quart, request, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI
import logging
from utils.utils import get_schema, get_llm_response

from redash_toolbelt import Redash
from redashAPI import RedashAPIClient

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

app = Quart(__name__)

# Set the logging level to INFO so that we can see the logs in the console
logging.basicConfig(level=logging.INFO)

# FOR TESTING PURPOSES
query_example = "SELECT \"Content type_Videos\", \"Device type_Mobile phone\", date FROM youtube_data_schema.youtube_chart_data LIMIT 10;"

def run() -> None:
    app.run(port=5057)

client = OpenAI(api_key=VARIABLE_KEY)

@app.route('/api/chat/echo')
async def echo():
    value = await request.get_json()
    question = value.get('question')
    response_data = {"answer": question }
    return jsonify(response_data), 200

@app.route('/api/chat', methods=['POST'])
async def handle_user_question():
    try:
        schema = get_schema()
        logging.info(schema)


        value = await request.get_json()
        question = value.get('question')

        answer = get_llm_response(question)

        visualize_results = visualize(query_example)

        logging.info(visualize_results)


        response_data = {"answer": answer}
        return jsonify(response_data), 200
    except Exception as error:
        print(error)
        logging.error(error)
        return jsonify({"error": "An error occurred"}), 500

@app.route('/api/chat/redash/data_sources', methods=['get'])
async def get_queries():
    logging.info(REDASH_API_KEY)
    queries = redash.get_data_sources()
    return jsonify(queries), 200

# @app.route('/api/chat/query', methods=['post'])
# async def create_dashboard_with_visualizations():
#     queries = redash.create_query()
#     return jsonify(queries), 200


@app.route('/api/chat/query_results', methods=['post'])
async def get_query_results():
    value = await request.get_json()
    query = value.get('query')

    # query = redash.get_query(query_id)
    # Execute the query and get the results
    results = redash.create_query(query)

    return jsonify(results), 200

@app.route('/api/chat/results', methods=['get'])
async def get_results():
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

    results = RedashApi.create_query(1, "Query 1", query)
    data = results.json()

    query_id = data.get('id')

    logging.info(query_id)

    visualization_results = RedashApi.create_visualization(
        query_id,
        "column",
        "Youtube visualizations",
        x_axis="date",
        y_axis=[
            {
                "name": "Content type_Videos",
                "type": "column",
                "label": "Geography DE"
            },
            {
                "name": "Device type_Mobile phone",
                "type": "column",
                "label": "Mobile Phone Views"
            }
        ]
    )

    # Get the visualization id
    viz_id = visualization_results.json().get('id')

    # Create the dashboard for where to add visualizations
    dashboard_results = RedashApi.create_dashboard(
        "Youtube Data Dashboard",
    )

    # Get the dashboard id
    ds_id = dashboard_results.json().get('id')


    # Widget for the visualization
    widget_results = redash.create_widget(
        ds_id,
        viz_id,
        "The youtube views visualization results",
        options={}
    )

    ids = {
        "query_id": query_id,
        "visualization_id": viz_id,
        "dashboard_id": ds_id,
        # "widget_id": widget_results.json().get('id')
    }

    return ids


# @app.route('/api/chat/visualize', methods=['post'])
# async def visualize(query: str):
#     value = await request.get_json()
#     query = value.get('query')
#
#     results = RedashApi.create_query(1, "Query 1", query)
#     data = results.json()
#
#     query_id = data.get('id')
#
#     logging.info(query_id)
#
#     visualization_results = RedashApi.create_visualization(
#         query_id,
#         "column",
#         "Youtube visualizations",
#         x_axis="date",
#         y_axis=[
#             {
#                 "name": "Content type_Videos",
#                 "type": "column",
#                 "label": "Geography DE"
#             },
#             {
#                 "name": "Device type_Mobile phone",
#                 "type": "column",
#                 "label": "Mobile Phone Views"
#             }
#         ]
#     )
#
#     # Get the visualization id
#     viz_id = visualization_results.json().get('id')
#
#     # Create the dashboard for where to add visualizations
#     dashboard_results = RedashApi.create_dashboard(
#         "Youtube Data Dashboard",
#     )
#
#     # Get the dashboard id
#     ds_id = dashboard_results.json().get('id')
#
#
#     # Widget for the visualization
#     widget_results = redash.create_widget(
#         ds_id,
#         viz_id,
#         "The youtube views visualization results",
#         options={}
#     )
#
#     ids = {
#         "query_id": query_id,
#         "visualization_id": viz_id,
#         "dashboard_id": ds_id,
#         # "widget_id": widget_results.json().get('id')
#     }
#
#     return jsonify(ids), 200




# TODO - Add quart schema
# TODO - Perform Testing
####################################################
# CELERY TASKS IMPLEMENTATION - REDASH API
####################################################




# @app.route('/api/chat/start_task', methods=['post'])
# async def start_task():
#     value = await request.get_json()
#     query = value.get('query')
#     task = long_running_taks.delay(query)
#     return jsonify({"task_id": task.id}), 200

# Example of processing the results
