from quart import Quart, request, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI

app = Quart(__name__)

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
        value = await request.get_json()
        question = value.get('question')
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a redash visualization assistant, skilled in SQL queries and data visualization. You are only required to give answers for query and data visualization questions. If asked about a topic outside these two, make sure to respond that you have no information regarding that question. I am only here to help you with your query and data visualization questions. When asked to write queries, only provide the code without descriptions."},
                {"role": "user", "content": question}
            ]
        )
        answer = completion.choices[0].message.content
        response_data = {"answer": answer}
        return jsonify(response_data), 200
    except Exception as error:
        print(error)
        return jsonify({"error": "An error occurred"}), 500

# TODO - Add quart schema

# TODO - Perform Testing
