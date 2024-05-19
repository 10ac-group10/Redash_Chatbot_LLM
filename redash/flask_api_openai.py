import os

import openai
from flask import Flask, render_template, request

app = Flask(__name__)

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")


# Define the default route to return the index.html file

@app.route("/")
def index():
    return render_template("index.html")


# Define the route to return the index.html file
@app.route("/chat", methods=["POST"])
def api():
    # Get the message from the request
    message = request.form["message"]

    # Send the message to OpenAI's API and receive the response
    # Call the OpenAI API to get the response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    # Return the response from the API
    return completion.choices[0].message.content


if __name__ == "__main__":
    app.run()
