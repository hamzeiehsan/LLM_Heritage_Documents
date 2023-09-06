from flask import Flask, jsonify, request
import VisualizationServices as vs
import QAServices as qas
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/get_all_models', methods=['GET'])
def all_reports():
    if request.method == 'GET':
        data = vs.fetch_all_reports()
        print(data)
        return jsonify(data)


@app.route('/ask_from_all_docs', methods=['GET'])
def qa():
    if request.method == 'GET':
        question = request.args.get("question")
        data = qas.ask_from_all_documents(question)
        print(data)
        return data


if __name__ == '__main__':
    app.run(debug=True)
