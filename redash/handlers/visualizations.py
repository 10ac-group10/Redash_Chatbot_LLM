from flask import request

from redash import models
from redash.handlers.base import BaseResource, get_object_or_404
from redash.permissions import (
    require_object_modify_permission,
    require_permission,
)
from redash.serializers import serialize_visualization


class VisualizationListResource(BaseResource):
    @require_permission("edit_query")
    def post(self):
        kwargs = request.get_json(force=True)

        query = get_object_or_404(models.Query.get_by_id_and_org, kwargs.pop("query_id"), self.current_org)
        require_object_modify_permission(query, self.current_user)

        kwargs["query_rel"] = query

        vis = models.Visualization(**kwargs)
        models.db.session.add(vis)
        models.db.session.commit()
        return serialize_visualization(vis, with_query=False)

import psycopg2
from psycopg2 import sql
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load the OpenAI API key from the environment
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the OpenAI object
llm = OpenAI(openai_api_key=api_key)

# Function to get the schema from the database
def get_schema():
    # Connect to your database
    conn = psycopg2.connect(database="your_database", user="your_username", password="your_password", host="127.0.0.1", port="5432")
    cur = conn.cursor()

    # Query the information_schema to get the schema
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
    """)import psycopg2
from psycopg2 import sql
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load the OpenAI API key from the environment
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the OpenAI object
llm = OpenAI(openai_api_key=api_key)

# Function to get the schema from the database
def get_schema():
    # Connect to your database
    conn = psycopg2.connect(database="your_database", user="your_username", password="your_password", host="127.0.0.1", port="5432")
    cur = conn.cursor()

    # Query the information_schema to get the schema
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
    """)

    # Format the schema into a string
    schema = "We have a database with the following tables:\n"
    for row in cur.fetchall():
        schema += f"- {row[0]}: Contains information about the {row[0]}. Columns: {row[1]} ({row[2]}).\n"

    return schema

# Get the schema string
schema = get_schema()

# Create a PromptTemplate from the schema
schema_prompt = PromptTemplate.from_template(schema)

# Chain the schema PromptTemplate and the OpenAI object together
llm_chain = schema_prompt | llm

# Now you can use this chain to ask questions to the model
question = "What is the average price of the products ordered by user with id 1?"
response = llm_chain.invoke(question)

# The response variable now contains the response from the OpenAI API. You can send this response back to the user.

    # Format the schema into a string
    schema = "We have a database with the following tables:\n"
    for row in cur.fetchall():
        schema += f"- {row[0]}: Contains information about the {row[0]}. Columns: {row[1]} ({row[2]}).\n"

    return schema

# Get the schema string
schema = get_schema()

# Create a PromptTemplate from the schema
schema_prompt = PromptTemplate.from_template(schema)

# Chain the schema PromptTemplate and the OpenAI object together
llm_chain = schema_prompt | llm

# Now you can use this chain to ask questions to the model
question = "What is the average price of the products ordered by user with id 1?"
response = llm_chain.invoke(question)

# The response variable now contains the response from the OpenAI API. You can send this response back to the user.
class VisualizationResource(BaseResource):
    @require_permission("edit_query")
    def post(self, visualization_id):
        vis = get_object_or_404(models.Visualization.get_by_id_and_org, visualization_id, self.current_org)
        require_object_modify_permission(vis.query_rel, self.current_user)

        kwargs = request.get_json(force=True)

        kwargs.pop("id", None)
        kwargs.pop("query_id", None)

        self.update_model(vis, kwargs)
        d = serialize_visualization(vis, with_query=False)
        models.db.session.commit()
        return d

    @require_permission("edit_query")
    def delete(self, visualization_id):
        vis = get_object_or_404(models.Visualization.get_by_id_and_org, visualization_id, self.current_org)
        require_object_modify_permission(vis.query_rel, self.current_user)
        self.record_event(
            {
                "action": "delete",
                "object_id": visualization_id,
                "object_type": "Visualization",
            }
        )
        models.db.session.delete(vis)
        models.db.session.commit()
