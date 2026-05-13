from flask import Flask, request, redirect, url_for
import json
from google.cloud import firestore

db = 'YOUR_DATABASE_NAME'  # sostituisci con il nome del tuo database Firestore
db = firestore.Client.from_service_account_json('secret.json', database=db)
# db = firestore.Client(database=db)  # usare questa riga quando deployato su Google App Engine

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('static', filename='index.html'))

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('static', filename='graph.html'))

@app.route('/graph', methods=['GET'])
def graph():
    return redirect(url_for('static', filename='graph.html'))


@app.route('/sensors', methods=['GET'])
def sensors():
    coll = 'sensor-readings'
    sensor_names = set()
    for entity in db.collection(coll).stream():
        sensor_names.add(entity.to_dict()['sensor'])
    return json.dumps(list(sensor_names)), 200


@app.route('/sensors/<s>', methods=['POST'])
def add_data(s):
    data = request.values['data']
    val = json.loads(request.values['val'])
    coll = 'sensor-readings'
    id = f'{s}-{data}'
    doc_ref = db.collection(coll).document(id)  # id can be omitted and it will be generated automatically
    doc_ref.set({'sensor': s, 'values': val, 'timestamp': data})
    print(doc_ref.get().id)
    return 'ok', 200


@app.route('/sensors/<s>', methods=['GET'])
def get_data(s):
    coll = 'sensor-readings'
    r = {}
    for entity in db.collection(coll).where('sensor', '==', s).stream():
        e = entity.to_dict()
        r[e['timestamp']] = e['values']
    # sort r by timestamp
    r = dict(sorted(r.items(), key=lambda item: item[0]))
    # convert r to list of list with index as first element and value as second element
    r = [[i, key, r[key]] for i, key in enumerate(r)]
    return json.dumps(r), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
