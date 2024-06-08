from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pymongo
import random
import json
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient('mongodb://localhost:27017/')
vocab = client['language']['vocab']
snippets = client['language']['snippets']
USER_SETTINGS_COLLECTION = client['language']['user_settings']

def getBestVocab(N=20, num_parents=2):
    '''
    Gets the N best vocab words (common words that need practicing).
    '''
    goodVocab = list(
        vocab.find({}, {'_id': 0}).sort([
            ('rep_data.next_review', 1),
            ('word_freq', -1)
        ])
        .limit(N)
    )

    goodParentIDs = []
    for doc in goodVocab:
        parents = doc['parents']
        random.shuffle(parents)

        goodParentIDs.extend(parents[:num_parents])

    print(f"Finding snippets for {len(goodParentIDs)} parent IDs")
    goodSnippets = list(snippets.find({'id': {'$in': goodParentIDs}}, {'_id': 0}))

    return {
        'vocab': goodVocab,
        'snippets': goodSnippets
    }


@app.route('/snippets', methods=['GET'])
@cross_origin()
def getSnippets():
    if request.method == 'GET':
        N = int(request.args.get('N', 20))
        num_parents = int(request.args.get('num_parents', 2))

        if (N < 0) or (num_parents < 0):
            return jsonify({'error': 'Negative number args are not allowed.'}), 400

        print(f"Got request for {N} snippets ({num_parents} parents each)")
        return jsonify(getBestVocab(N=N, num_parents=num_parents))

@app.route('/next_media_snippet', methods=['GET'])
@cross_origin()
def getNextSnippet():
    '''
    Get the next snippet in the specific media.
    NOTE: Should be the id of the snippet, not the mongo _id.
    '''
    if request.method == 'GET':
        if 'id' not in request.args:
            return jsonify({'error': 'No id provided.'}), 400
        currentSnippetId = request.args.get('id')

        # Query db for the current snippet
        currentSnippet = snippets.find_one({'id': currentSnippetId})
        processed = json.loads(json_util.dumps(currentSnippet))

        # Get the next snippet
        currentMediaIndex = processed['media_index']
        currentMediaPath = processed['source_path']

        nextSnippetDoc = snippets.find_one({
            'media_index': currentMediaIndex + 1,
            'source_path': currentMediaPath
        })

        # TODO: Add a check here to determine if there really are no more snippets from the source.
        if not nextSnippetDoc:
            return jsonify({'error': 'No next snippet found.'}), 404

        processedNext = json.loads(json_util.dumps(nextSnippetDoc))

        return jsonify(processedNext)

@app.route('/user', methods=['GET'])
@cross_origin()
def handleUser():
    userId = request.args.get('id')
    if not userId:
        return jsonify({'error': 'No user id provided.'}), 400

    try:
        userBsonId = ObjectId(userId)
    except:
        return jsonify({
            'error': 'Invalid user id provided. Must be a valid monog ObjectId format.'
        }), 400

    try:
        userDoc = USER_SETTINGS_COLLECTION.find_one({'_id': userBsonId})
    except:
        return jsonify({
            'error': f'Error querying for user document with id: {userId}'
        }), 500

    if not userDoc:
        return jsonify({'error': f'No user found with id: {userId}'}), 404

    return jsonify(json.loads(json_util.dumps(userDoc)))


if __name__ == '__main__':
    app.run(debug=True)