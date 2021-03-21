import os
import pycurl

from pprint import pprint
from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
from elasticsearch import Elasticsearch
from bert_serving.client import BertClient
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlencode

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
    
SEARCH_SIZE = 100
INDEX_NAME = os.environ['INDEX_NAME']
INDEX_BERT_NAME = os.environ['INDEX_BERT_NAME']
GENERIC_PWORD = os.environ.get('DEFUSR')
ADMIN_PWORD = os.environ.get('BERTADM')
KICKOFF_URL = os.environ.get('KICKOFF_URL')
ES_ENDPOINT = os.environ.get('ES_ENDPOINT')
BERT_ENDPOINT = os.environ.get('BERT_ENDPOINT')
app = Flask(__name__, static_folder='static')
auth = HTTPBasicAuth()


users = {
    "generic": generate_password_hash(GENERIC_PWORD),
    "berttestadm": generate_password_hash(ADMIN_PWORD),
}

roles = {
    "generic": "user",
    "berttestadm": ["user", "admin"],
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
        
@auth.get_user_roles
def get_user_roles(user):
    return roles[user]
    
@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)
    
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/startjob')
@auth.login_required(role='admin')
def kickoff_job():
    job = request.args.get('job')
       
    if len(job) > 0 and len(job) < 20:
        c = pycurl.Curl()
        c.setopt(c.URL,KICKOFF_URL)
        post_data = {'project': 'githubspd', 'spider': job}
        postfields = urlencode(post_data)
        c.setopt(c.POSTFIELDS, postfields)
        buffer = BytesIO()
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        
        if c.getinfo(c.RESPONSE_CODE) == 200:
            c.close()
            response = make_response("JOB STARTED", 200)
            response.mimetype = "text/plain"
        else:
            c.close()
            response = make_response("SCRAPYD ERROR", 500)
            response.mimetype = "text/plain" 
    else:
        response = make_response("JOB NAME ERROR", 500)
        response.mimetype = "text/plain"        
    
    return response    
        
@app.route('/createindex')
@auth.login_required(role='admin')
def create_index():
    client = Elasticsearch(ES_ENDPOINT)
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
@auth.login_required
def analyzerbert():
    bc = BertClient(ip=BERT_ENDPOINT, output_fmt='list')
    client = Elasticsearch(ES_ENDPOINT)

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
@auth.login_required
def analyzer():
    client = Elasticsearch(ES_ENDPOINT)

    query = request.args.get('q')

    script_query = {
       "bool": {
         "must": {
           "match": {
             "text": query
           }
         }
       }
    }

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["title", "url", "text"]}
        }
    )
    print(query)
    pprint(response)
    return jsonify(response)


if __name__ == '__main__':
    app.run()
