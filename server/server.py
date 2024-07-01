from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pymongo
import random
import json
from bson import json_util
from bson.objectid import ObjectId
import time
import heapq
import math

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = pymongo.MongoClient('mongodb://localhost:27017/')
VOCAB_COLLECTION = client['language']['vocab']
SNIPPETS_COLLECTION = client['language']['snippets']
USER_SETTINGS_COLLECTION = client['language']['user_settings']

DEFAULT_USER_SETTINGS = {
    "repetition_constants": {
        "S": 2670,
        "curve_shapes": {
            "again": 1,
            "hard": 2,
            "good": 4,
            "easy": 6,
        }
    },
}

def getBestVocab(N=20, num_parents=2):
    '''
    Gets the N best vocab words (common words that need practicing).
    '''
    goodVocab = list(
        VOCAB_COLLECTION.find({}, {'_id': 0}).sort([
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
    goodSnippets = list(SNIPPETS_COLLECTION.find({'id': {'$in': goodParentIDs}}, {'_id': 0}))

    return {
        'vocab': goodVocab,
        'snippets': goodSnippets
    }

def updateMatchingPaths(src, target, path=None):
    if path is None:
        path = []

    for key, value in src.items():
        currPath = path + [key]
        if key in target:
            if isinstance(value, dict) and isinstance(target[key], dict):
                updateMatchingPaths(value, target[key], path=currPath)
            else:
                if type(value) == type(target[key]):
                    target[key] = value
        else:
            if isinstance(value, dict):
                if key not in target:
                    target[key] = {}
                updateMatchingPaths(value, target[key], path=currPath)

def repDataCurveEquation(timeDelta, S, alpha):
    return math.e ** (-timeDelta / (alpha * S))


### API ROUTES ###

# Snippet endpoints

@app.route('/snippets', methods=['GET'])
@cross_origin()
def getSnippets():
    if request.method == 'GET':
        N = int(request.args.get('N', 20))
        num_parents = int(request.args.get('num_parents', 2))

        if (N < 0) or (num_parents < 0):
            return jsonify(
                {'error': 'Negative number args are not allowed.'},
            ), 400

        print(f"Got request for {N} snippets ({num_parents} parents each)")
        return jsonify(
            getBestVocab(N=N, num_parents=num_parents),
        ), 200

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
        currentSnippet = SNIPPETS_COLLECTION.find_one({'id': currentSnippetId})
        processed = json.loads(json_util.dumps(currentSnippet))

        # Get the next snippet
        currentMediaIndex = processed['media_index']
        currentMediaPath = processed['source_path']

        nextSnippetDoc = SNIPPETS_COLLECTION.find_one({
            'media_index': currentMediaIndex + 1,
            'source_path': currentMediaPath
        })

        # TODO: Add a check here to determine if there really are no more snippets from the source.
        if not nextSnippetDoc:
            return jsonify({'error': 'No next snippet found.'}), 404

        processedNext = json.loads(json_util.dumps(nextSnippetDoc))

        return jsonify(processedNext), 200


# User API endpoints

def getUserDoc(userName=None, userId=None):
    if not userId and not userName:
        return jsonify({'error': 'No username or id provided.'}), 400

    # Build query by username or user id
    if userId:
        try:
            userBsonId = ObjectId(userId)
            query = {'_id': userBsonId}
        except:
            return jsonify({
                'error': 'Invalid user id provided. Must be a valid monog ObjectId format.'
            }), 400
    elif userName:
        query = {'username': userName}

    # Query for user doc
    try:
        userDoc = USER_SETTINGS_COLLECTION.find_one(query)
    except:
        return jsonify({
            'error': f'Error querying for user document with id: {userId}'
        }), 500

    if not userDoc:
        return jsonify({'error': f'No user found with id: {userId}'}), 404

    # Return result
    return jsonify(
        json.loads(json_util.dumps(userDoc)),
    ), 200

@app.route('/user', methods=['GET'])
@cross_origin()
def getUser():
    userId = request.args.get('id')
    userName = request.args.get('username')

    return getUserDoc(userName=userName, userId=userId)

@app.route('/user', methods=['PUT'])
@cross_origin()
def updateUser():
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

    # Get updated params from request body
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided.'}), 400
    print(f'found body data: {data}')
    print(dir(request))

    # Recursively walk the request body and update if the old doc has a matching key
    updateMatchingPaths(data, userDoc)

    # Update the user document
    result = USER_SETTINGS_COLLECTION.update_one({'_id': userBsonId}, {'$set': userDoc}).raw_result

    return jsonify({
        'result': result,
    }), 200

@app.route('/user', methods=['POST'])
@cross_origin()
def postUser():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username provided. (required query param)'}), 400

    # Check that username isn't taken
    existingUser = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if existingUser:
        return jsonify({'error': f'Username already taken: {username}'}), 400

    # Create new user
    newUser = DEFAULT_USER_SETTINGS
    newUser['username'] = username

    # Insert new user
    result = USER_SETTINGS_COLLECTION.insert_one(newUser)

    return jsonify({
        'id': str(result.inserted_id),
    }), 200


# Spaced rep data endpoints

def updateVocabItem(vocabId, strength, reviewTime, userDiffs):
    try:
        vocabDoc = VOCAB_COLLECTION.find_one({'id': vocabId})

        if not vocabDoc:
            return 204

        # Update the vocab item
        repData = vocabDoc['rep_data']
        newData = repData.copy()
        strengthValue = userDiffs[strength]
        if repData['history_length'] == 0:
            # First exposure. Set everything to defaults.
            newData['last_review'] = reviewTime
            newData['last_strength'] = strength
            newData['average_strength'] = strengthValue
            newData['history_length'] = 1
            newData['history'] = [
                {
                    'strength': strength,
                    'time': reviewTime,
                }
            ]
        else:
            # Compute new values
            newData['last_review'] = reviewTime
            newData['last_strength'] = strength
            newData['average_strength'] = (
                (repData['average_strength'] * repData['history_length']) + strengthValue
            ) / (repData['history_length'] + 1)
            newData['history_length'] += 1
            newData['history'].append({
                'strength': strength,
                'time': reviewTime,
            })

        # Update the doc
        result = VOCAB_COLLECTION.update_one({'id': vocabId}, {'$set': {'rep_data': newData}})

        # return result.modified_count == 1
        return 200
    except Exception as e:
        print(f'Error updating vocab item: {vocabId}')
        print(e)
        return 422

@app.route('/rep', methods=['POST'])
@cross_origin()
def logVocabLearning():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username provided. (required query param)'}), 400

    userSettings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if not userSettings:
        return jsonify({'error': f'Cannot update vocab. No user found with username: {username}'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided.'}), 400

    # Get difficulty for user
    userSettings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    print(f'Found user settings doc: {userSettings}')

    userDiffs = userSettings['repetition_constants']['curve_shapes']

    print(f'found body data: {json.dumps(data, indent=2)}');
    codes = set()
    updateStatuses = []
    for vId in data['vocab']:
        updateResult = updateVocabItem(
            vId,
            strength=data['strength'],
            reviewTime=data['review_time'],
            userDiffs=userDiffs,
        )
        message = ''
        if updateResult == 200:
            message = 'Successfully updated vocab item'
        elif updateResult == 204:
            message = 'Failed to find vocab item'
        elif updateResult == 422:
            message = 'Failed to update vocab item'
        response = {
            'id': vId,
            'status': updateResult,
            'message': message,
        }
        updateStatuses.append(response)
        codes.add(updateResult)

    # Full success/fail/missing
    if len(codes) == 1:
        if 200 in codes:
            return jsonify({'success': True}), 200
        elif 204 in codes:
            return jsonify({'error': 'All provoided vocab items were not in the db\'s vocab set'}), 204
        elif 422 in codes:
            return jsonify({'error': 'Failed to update any vocab items.'}), 422

    # Mixed results
    return jsonify(results=updateStatuses), 207

@app.route('/rep', methods=['GET'])
@cross_origin()
def getRepItems():
    DEFAULT_N = 10
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username provided. (required query param)'}), 400

    rankTypes = ['recent', 'average']
    rankType = request.args.get('rank_type', 'recent')
    if rankType not in rankTypes:
        return jsonify({'error': f'Invalid rank type. Must be one of: {rankTypes} (defaults to recent)'}), 400

    try:
        N = int(request.args.get('N', DEFAULT_N))
    except:
        return jsonify({'error': 'Invalid N provided. Must be an integer.'}), 400

    currTime = time.time()

    userSettings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if not userSettings:
        return jsonify({'error': f'Cannot get vocab. No user found with username: {username}'}), 404

    userS = userSettings['repetition_constants']['S']
    userDiffs = userSettings['repetition_constants']['curve_shapes']

    # Get all the seen vocab items
    query = {
        'rep_data.last_review': {'$ne': None}
    }
    documents = VOCAB_COLLECTION.find(query)
    # count = VOCAB_COLLECTION.count_documents(query)

    # Compute the rank values
    heap = []
    for doc in documents:
        repData = doc['rep_data']
        timeDelta = currTime - repData['last_review']

        if rankType == 'recent':
            lastStrength = repData['last_strength']
            alpha = userDiffs[lastStrength]
            rankValue = repDataCurveEquation(timeDelta, userS, alpha)
        elif rankType == 'average':
            historyValues = [userDiffs[item['strength']] for item in repData['history']]
            avgAlpha = sum(historyValues) / len(historyValues)
            rankValue = repDataCurveEquation(timeDelta, userS, avgAlpha)

        item = doc['id']
        if len(heap) < N:
            heapq.heappush(heap, (-rankValue, item))
        else:
            heapq.heappushpop(heap, (-rankValue, item))

    try:
        # Choose a random parent for each vocab item
        snippetSet = set()
        for (rank, vId) in heap:
            vocabDoc = VOCAB_COLLECTION.find_one({'id': vId})
            parents = vocabDoc['parents']
            random.shuffle(parents)
            while parents and parents[0] in snippetSet:
                parents.pop(0)
            if parents:
                snippetSet.add(parents[0])

        # Get the snippets
        snippets = list(SNIPPETS_COLLECTION.find(
            { 'id': {'$in': list(snippetSet)} },
            { '_id': 0 }
        ))

        return jsonify({
            'status': 'success',
            'vocab': heap,
            'snippets': snippets,
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to get snippets.',
            'exception': str(e),
        }), 500

if __name__ == '__main__':
    app.run(debug=True)