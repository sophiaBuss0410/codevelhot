from flask import Flask, request, jsonify

from models.rag_client import MyQdrantClient
from helpers import read_config


app = Flask(__name__)
config = read_config("config.yaml")
rag_client = MyQdrantClient(config)

@app.route('/post-data', methods=['POST'])
def post_data():
    text_data = request.args.get('text', '')
    print("text_data: ", text_data)
    rag_data = rag_client.get_top_matches_by_query(text_data)
    return jsonify(rag_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
