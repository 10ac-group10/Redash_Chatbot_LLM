from dotenv import load_dotenv
from flask import request, jsonify
from redash.handlers.base import (
    BaseResource
)
import os
from langchain_openai import OpenAI
from langchain_core.prompts import SystemMessagePromptTemplate

from src.utils import get_schema

load_dotenv()

VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")

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
    system_message = f"You are a nice assistant. You are trained to generate SQL queries for Redash based on user's questions. An example is this: {sql_query_example}. But it must note be exact like that. Just note that the table names are enclosed in double quotations and the part after 'FROM'. \nYou are not to make up any information, if you don't know, say 'I don't know'. The date field has values in this format: YYYY-MM-DD. You have access to the youtube database with the following schema:\n" + schema

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

class ChatResource(BaseResource):
    def post(self):
        try:
            value = request.get_json()
            question = value.get('question')

            answer = get_llm_response(question)

            response_data = {"answer": answer}
            return jsonify(response_data), 200
        except Exception as error:
            print(error)
            return jsonify({"error": "An error occurred"}), 500
