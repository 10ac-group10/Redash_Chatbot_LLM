from quart import Quart, jsonify

app = Quart(__name__)

@app.route('/')
async def hello():
    return jsonify(message="Hello, World!")

if __name__ == "__main__":
    app.run(port=5000)
