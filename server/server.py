from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import random

app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient('mongodb://localhost:27017/')
vocab = client['language']['vocab']
snippets = client['language']['snippets']

def getBestVocab(N_vocab=20):
    goodVocab = list(
        vocab.find({}, {'_id': 0}).sort([
            ('rep_data.next_review', 1),
            ('word_freq', -1)
        ])
        .limit(N_vocab)
    )

    goodParentIDs = []
    for doc in goodVocab:
        parents = doc['parents']
        random.shuffle(parents)

        goodParentIDs.extend(parents[:2])
    

    print(f"Finding snippets for {len(goodParentIDs)} parent IDs")
    goodSnippets = list(snippets.find({'id': {'$in': goodParentIDs}}, {'_id': 0}))

    return goodSnippets


@app.route('/snippets', methods=['GET'])
def getSnippets():
    if request.method == 'GET':
        return jsonify(getBestVocab())


if __name__ == '__main__':
    app.run(debug=True)