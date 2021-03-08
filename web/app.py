import os
from pprint import pprint

from flask import Flask, render_template, jsonify, request, send_from_directory
from elasticsearch import Elasticsearch
from bert_serving.client import BertClient
SEARCH_SIZE = 100
INDEX_NAME = os.environ['INDEX_NAME']
INDEX_BERT_NAME = os.environ['INDEX_BERT_NAME']
app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bert')
def bert():
    return render_template('bertsearchtemp.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)
    
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/createindex')
def create_index():
    client = Elasticsearch('elasticsearch:9200')
    client.indices.delete(index=INDEX_NAME, ignore=[404])
    client.indices.delete(index=INDEX_BERT_NAME, ignore=[404])
    with open('simpleindex.json') as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME, body=source)
    with open('bertindex.json') as bertindex_file:
        bertsource = bertindex_file.read().strip()
        client.indices.create(index=INDEX_BERT_NAME, body=bertsource)
    return render_template('bertsearchtemp.html')
    
@app.route('/searchbert')
def analyzerbert():
    bc = BertClient(ip='bertserving', output_fmt='list')
    client = Elasticsearch('elasticsearch:9200')

    query = request.args.get('q')
    query_vector = bc.encode([query])[0]

    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['text_vector']) + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    response = client.search(
        index=INDEX_BERT_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["title", "url", "text"]}
        }
    )
    print(query)
    pprint(response)
    return jsonify(response)


@app.route('/searchsimple')
def analyzer():
    client = Elasticsearch('elasticsearch:9200')

    query = request.args.get('q')

    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "doc['text']",
                "params": {"query": query}
            }
        }
    }

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["title", "text"]}
        }
    )
    print(query)
    pprint(response)
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
