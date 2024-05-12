from quart import Quart, request, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI
import logging
from utils.utils import get_schema, get_llm_response

app = Quart(__name__)

logging.basicConfig(level=logging.INFO)

load_dotenv()

VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")

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

# TODO - Add quart schema

# TODO - Perform Testing
