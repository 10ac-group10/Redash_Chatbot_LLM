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

# Define the URL of the Redash instance - In this case, it is the URL of nginx which is the reverse proxy for the Redash server and quart server
REDASH_URL = "http://nginx:80"

# Initialize the Redash object that will be used to interact with the Redash API
redash = Redash(REDASH_URL, REDASH_API_KEY)
RedashApi = RedashAPIClient(REDASH_API_KEY, REDASH_URL)

app = Quart(__name__)

# Set the logging level to INFO so that we can see the logs in the console
logging.basicConfig(level=logging.INFO)

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

    query = "SELECT geography_de, 'Device type_Mobile phone', date FROM youtube_data_schema.youtube_chart_data WHERE geography_de > 1"

    # query = redash.get_query(query_id)
    # Execute the query and get the results
    results = redash.create_query(query)

    return jsonify(results), 200

@app.route('/api/chat/results', methods=['get'])
async def get_results():
    # Execute the query and get the results
    query = "SELECT geography_de, 'Device type_Mobile phone', date FROM youtube_data_schema.youtube_chart_data WHERE geography_de > 1"

    results = RedashApi.query_and_wait_result(1, query)

    return jsonify(results), 200

# TODO - Add quart schema
# TODO - Perform Testing
