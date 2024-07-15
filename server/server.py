import random
import json
import time
import heapq
import math

import pymongo
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from bson import json_util
from bson.objectid import ObjectId

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

def get_best_vocab(n=20, num_parents=2):
    '''
    Gets the n best vocab words (common words that need practicing).
    '''
    good_vocab = list(
        VOCAB_COLLECTION.find({}, {'_id': 0}).sort([
            ('rep_data.next_review', 1),
            ('word_freq', -1)
        ])
        .limit(n)
    )

    good_parent_ids = []
    for doc in good_vocab:
        parents = doc['parents']
        random.shuffle(parents)

        good_parent_ids.extend(parents[:num_parents])

    print(f"Finding snippets for {len(good_parent_ids)} parent IDs")
    good_snippets = list(SNIPPETS_COLLECTION.find({'id': {'$in': good_parent_ids}}, {'_id': 0}))

    return {
        'vocab': good_vocab,
        'snippets': good_snippets
    }

def update_matching_paths(src, target, path=None):
    if path is None:
        path = []

    for key, value in src.items():
        curr_path = path + [key]
        if key in target:
            if isinstance(value, dict) and isinstance(target[key], dict):
                update_matching_paths(value, target[key], path=curr_path)
            else:
                if type(value) == type(target[key]):
                    target[key] = value
        else:
            if isinstance(value, dict):
                if key not in target:
                    target[key] = {}
                update_matching_paths(value, target[key], path=curr_path)

def rep_data_curve_equation(time_delta, s, alpha):
    return math.e ** (-time_delta / (alpha * s))


### API ROUTES ###

# Snippet endpoints

@app.route('/snippets', methods=['GET'])
@cross_origin()
def get_snippets():
    if request.method == 'GET':
        n = int(request.args.get('n', 20))
        num_parents = int(request.args.get('num_parents', 2))

        if (n < 0) or (num_parents < 0):
            return jsonify(
                {'error': 'Negative number args are not allowed.'},
            ), 400

        print(f"Got request for {n} snippets ({num_parents} parents each)")
        return jsonify(
            get_best_vocab(n=n, num_parents=num_parents),
        ), 200

@app.route('/next_media_snippet', methods=['GET'])
@cross_origin()
def get_next_snippet():
    '''
    Get the next snippet in the specific media.
    NOTE: Should be the id of the snippet, not the mongo _id.
    '''
    if request.method == 'GET':
        if 'id' not in request.args:
            return jsonify({'error': 'No id prov_ided.'}), 400
        current_snippet_id = request.args.get('id')

        # Query db for the current snippet
        current_snippet = SNIPPETS_COLLECTION.find_one({'id': current_snippet_id})
        processed = json.loads(json_util.dumps(current_snippet))

        # Get the next snippet
        current_media_index = processed['media_index']
        current_media_path = processed['source_path']

        next_snippet_doc = SNIPPETS_COLLECTION.find_one({
            'media_index': current_media_index + 1,
            'source_path': current_media_path
        })

        # TODO: Add a check here to determine if there really are no more snippets from the source.
        if not next_snippet_doc:
            return jsonify({'error': 'No next snippet found.'}), 404

        processed_next = json.loads(json_util.dumps(next_snippet_doc))

        return jsonify(processed_next), 200


# User API endpoints

def get_user_doc(user_name=None, user_id=None):
    if not user_id and not user_name:
        return jsonify({'error': 'No username or id prov_ided.'}), 400

    # Build query by username or user id
    if user_id:
        try:
            user_bson_id = ObjectId(user_id)
            query = {'_id': user_bson_id}
        except:
            return jsonify({
                'error': 'Invalid user id prov_ided. Must be a valid monog ObjectId format.'
            }), 400
    elif user_name:
        query = {'username': user_name}
    else:
        query = {}

    # Query for user doc
    try:
        user_doc = USER_SETTINGS_COLLECTION.find_one(query)
    except:
        return jsonify({
            'error': f'Error querying for user document with id: {user_id}'
        }), 500

    if not user_doc:
        return jsonify({'error': f'No user found with id: {user_id}'}), 404

    # Return result
    return jsonify(
        json.loads(json_util.dumps(user_doc)),
    ), 200

@app.route('/user', methods=['GET'])
@cross_origin()
def get_user():
    user_id = request.args.get('id')
    user_name = request.args.get('username')

    return get_user_doc(user_name=user_name, user_id=user_id)

@app.route('/user', methods=['PUT'])
@cross_origin()
def update_user():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'error': 'No user id prov_ided.'}), 400

    try:
        user_bson_id = ObjectId(user_id)
    except:
        return jsonify({
            'error': 'Invalid user id prov_ided. Must be a valid monog ObjectId format.'
        }), 400

    try:
        user_doc = USER_SETTINGS_COLLECTION.find_one({'_id': user_bson_id})
    except:
        return jsonify({
            'error': f'Error querying for user document with id: {user_id}'
        }), 500

    if not user_doc:
        return jsonify({'error': f'No user found with id: {user_id}'}), 404

    # Get updated params from request body
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data prov_ided.'}), 400
    print(f'found body data: {data}')
    print(dir(request))

    # Recursively walk the request body and update if the old doc has a matching key
    update_matching_paths(data, user_doc)

    # Update the user document
    result = USER_SETTINGS_COLLECTION.update_one(
        {
            '_id': user_bson_id
        },
        {
            '$set': user_doc
        }
    ).raw_result

    return jsonify({
        'result': result,
    }), 200

@app.route('/user', methods=['POST'])
@cross_origin()
def post_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username prov_ided. (required query param)'}), 400

    # Check that username isn't taken
    existing_user = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if existing_user:
        return jsonify({'error': f'Username already taken: {username}'}), 400

    # Create new user
    new_user = DEFAULT_USER_SETTINGS
    new_user['username'] = username

    # Insert new user
    result = USER_SETTINGS_COLLECTION.insert_one(new_user)

    return jsonify({
        'id': str(result.inserted_id),
    }), 200


# Spaced rep data endpoints

def update_vocab_item(vocab_id, strength, review_time, user_diffs):
    try:
        vocab_doc = VOCAB_COLLECTION.find_one({'id': vocab_id})

        if not vocab_doc:
            return 204

        # Update the vocab item
        rep_data = vocab_doc['rep_data']
        new_data = rep_data.copy()
        strength_value = user_diffs[strength]
        if rep_data['history_length'] == 0:
            # First exposure. Set everything to defaults.
            new_data['last_review'] = review_time
            new_data['last_strength'] = strength
            new_data['average_strength'] = strength_value
            new_data['history_length'] = 1
            new_data['history'] = [
                {
                    'strength': strength,
                    'time': review_time,
                }
            ]
        else:
            # Compute new values
            new_data['last_review'] = review_time
            new_data['last_strength'] = strength
            new_data['average_strength'] = (
                (rep_data['average_strength'] * rep_data['history_length']) + strength_value
            ) / (rep_data['history_length'] + 1)
            new_data['history_length'] += 1
            new_data['history'].append({
                'strength': strength,
                'time': review_time,
            })

        # Update the doc
        result = VOCAB_COLLECTION.update_one({'id': vocab_id}, {'$set': {'rep_data': new_data}})

        if result.modified_count == 1:
            return jsonify({'success': True}), 200

        return jsonify({
            'error': f'Failed to update single vocab item ({result.modified_count})'
        }), 500
    except Exception as e:
        print(f'Error updating vocab item: {vocab_id}')
        print(e)
        return 422

@app.route('/rep', methods=['POST'])
@cross_origin()
def log_vocab_learning():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username prov_ided. (required query param)'}), 400

    user_settings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if not user_settings:
        return jsonify({
            'error': f'Cannot update vocab. No user found with username: {username}'
        }), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data prov_ided.'}), 400

    # Get difficulty for user
    user_settings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    print(f'Found user settings doc: {user_settings}')

    user_diffs = user_settings['repetition_constants']['curve_shapes']

    print(f'found body data: {json.dumps(data, indent=2)}')
    codes = set()
    update_statuses = []
    for v_id in data['vocab']:
        update_result = update_vocab_item(
            v_id,
            strength=data['strength'],
            review_time=data['review_time'],
            user_diffs=user_diffs,
        )
        message = ''
        if update_result == 200:
            message = 'Successfully updated vocab item'
        elif update_result == 204:
            message = 'Vocab item not found in db'
        elif update_result == 422:
            message = 'Failed to update vocab item'
        response = {
            'id': v_id,
            'status': update_result,
            'message': message,
            'strength': data['strength'],
        }
        update_statuses.append(response)
        codes.add(update_result)

    # Full success/fail/missing
    if len(codes) == 1:
        if 200 in codes:
            return jsonify({'success': True}), 200
        if 204 in codes:
            return jsonify({
                'success': True,
                'message': 'All provoided vocab items were not in the db\'s vocab set',
            }), 204
        if 422 in codes:
            return jsonify({'error': 'Failed to update any vocab items.'}), 422

    # Mixed results
    mixed_response = {
        'codes': list(codes),
        'results': update_statuses,
        'strength': data['strength'],
    }
    return jsonify(mixed_response), 207

@app.route('/rep', methods=['GET'])
@cross_origin()
def get_rep_items():
    default_n = 10
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username prov_ided. (required query param)'}), 400

    rank_types = ['recent', 'average']
    rank_type = request.args.get('rank_type', 'recent')
    if rank_type not in rank_types:
        return jsonify({
            'error': f'Invalid rank type. Must be one of: {rank_types} (defaults to recent)'
        }), 400

    try:
        n = int(request.args.get('n', default_n))
    except:
        return jsonify({'error': 'Invalid n provided. Must be an integer.'}), 400

    curr_time = time.time()

    user_settings = USER_SETTINGS_COLLECTION.find_one({'username': username})
    if not user_settings:
        return jsonify({'error': f'Cannot get vocab. No user found with username: {username}'}), 404

    user_s = user_settings['repetition_constants']['S']
    user_diffs = user_settings['repetition_constants']['curve_shapes']

    # Get all the seen vocab items
    query = {
        'rep_data.last_review': {'$ne': None}
    }
    documents = VOCAB_COLLECTION.find(query)
    # count = VOCAB_COLLECTION.count_documents(query)

    # Compute the rank values
    heap = []
    for doc in documents:
        rep_data = doc['rep_data']
        time_delta = curr_time - rep_data['last_review']

        if rank_type == 'recent':
            last_strength = rep_data['last_strength']
            alpha = user_diffs[last_strength]
            rank_value = rep_data_curve_equation(time_delta, user_s, alpha)
        elif rank_type == 'average':
            history_values = [user_diffs[item['strength']] for item in rep_data['history']]
            avg_alpha = sum(history_values) / len(history_values)
            rank_value = rep_data_curve_equation(time_delta, user_s, avg_alpha)
        else:
            rank_value = 0

        item = doc['id']
        if len(heap) < n:
            heapq.heappush(heap, (-rank_value, item))
        else:
            heapq.heappushpop(heap, (-rank_value, item))

    try:
        # Choose a random parent for each vocab item
        snippet_set = set()
        # (rank, id) in heap
        for (_, v_id) in heap:
            vocab_doc = VOCAB_COLLECTION.find_one({'id': v_id})
            parents = vocab_doc['parents']
            random.shuffle(parents)
            while parents and parents[0] in snippet_set:
                parents.pop(0)
            if parents:
                snippet_set.add(parents[0])

        # Get the snippets
        snippets = list(SNIPPETS_COLLECTION.find(
            { 'id': {'$in': list(snippet_set)} },
            { '_id': 0 }
        ))

        return jsonify({
            'status': 'success',
            'vocab': heap,
            'snippets': snippets,
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get snippets.',
            'exception': str(e),
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
