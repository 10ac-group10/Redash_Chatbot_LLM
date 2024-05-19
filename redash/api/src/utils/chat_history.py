import json

import redis


def save_chat_history_redis(chat_history):
    # Connect to your Redis server
    r = redis.Redis(host='redis', port=6379, db=0)

    # Serialize the chat history to a JSON string
    chat_history_json = json.dumps(chat_history)

    # Store the chat history in Redis
    r.set('chat_history', chat_history_json)


def get_chat_history_redis():
    # Connect to your Redis server
    r = redis.Redis(host='redis', port=6379, db=0)

    # Retrieve the chat history from Redis
    chat_history_json = r.get('chat_history')

    # If chat_history_json is not None, deserialize it back into a Python object
    if chat_history_json is not None:
        chat_history = json.loads(chat_history_json)
        return chat_history

    # If chat_history_json is None, return an empty list or any other default value
    return []
