'''
This file are exchangable methods for dumping data somewhere.
Classes should be able to ingest a list of new snippets and sample items,
as well as return existing entrie ids.
'''

import json
import os
from abc import ABC, abstractmethod
import pymongo
from datetime import datetime, timedelta

class BaseInterface(ABC):
    '''
    This class is used to check that all interfaces have the required methods.
    '''
    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def existingSnippets(self):
        pass

    @abstractmethod
    def getSnippets(self, snippets=None):
        pass

    @abstractmethod
    def existingSamples(self):
        pass

    @abstractmethod
    def getSample(self, sample=None):
        pass

    @abstractmethod
    def ingestItems(self, snippetItems, sampleItems):
        pass


class LocalFiles(BaseInterface):
    def __init__(self, snippetsPath='./entries/entries.json', samplesPath='./entries/sample.json'):
        self.snippetsPath = snippetsPath
        self.samplesPath = samplesPath

        # Check file exists and is not empty
        if not os.path.exists(snippetsPath) or os.path.getsize(snippetsPath) == 0:
            print(f"Creating new entries file at {snippetsPath}")
            with open(snippetsPath, 'w') as file:
                file.write('{}')

        if not os.path.exists(samplesPath) or os.path.getsize(samplesPath) == 0:
            with open(samplesPath, 'w') as file:
                file.write('{}')

    def flush(self):
        print("FLUSHING THE DATABASE LOCAL FILE")
        with open(self.snippetsPath, 'w') as file:
            file.write('{}')

        with open(self.samplesPath, 'w') as file:
            file.write('{}')

    # Handle snippet items
    def existingSnippets(self):
        with open(self.snippetsPath) as file:
            existingEntries = json.load(file)
            return set(existingEntries.keys())

    def getSnippets(self, snippets=None):
        if snippets == None:
            snippets = self.existingSnippets()

        with open(self.snippetsPath) as file:
            existingEntries = json.load(file)
            return [existingEntries[idx] for idx in snippets]

    # Handle sample items
    def existingSamples(self):
        with open(self.samplesPath) as file:
            existingSample = json.load(file)
            return set(existingSample.keys())

    def getSample(self, sample=None):
        if sample == None:
            sample = self.existingSample()

        with open(self.samplesPath) as file:
            existingSample = json.load(file)
            return [existingSample[idx] for idx in sample]

    # Handle new items
    def ingestItems(self, snippetItems, sampleItems):
        '''
        This func assumes that the provided items are new to the collections
        '''
        # Process snippets
        with open(self.snippetsPath) as file:
            existingEntries = json.load(file)

        existingEntries.update(snippetItems)

        with open(self.snippetsPath, 'w') as file:
            json.dump(existingEntries, file)

        # Process sample
        with open(self.samplesPath) as file:
            existingSample = json.load(file)

        existingSample.update(sampleItems)

        with open(self.samplesPath, 'w') as file:
            json.dump(existingSample, file)


class MongoInterface(BaseInterface):
    def __init__(self, mongoURI):
        self.mongoURI = mongoURI
        self.client = pymongo.MongoClient(mongoURI)

        # TODO: Check if collections and db exist

        self.db = self.client['language']
        self.snippetsCollection = self.db['snippets']
        self.sampleCollection = self.db['samples']
        self.vocabCollection = self.db['vocab']

        self.SNIPPET_KEY = 'id'
        self.SAMPLE_KEY = 'specific_id'
        self.SAMPLE_VOCAB_POINTER_KEY = 'vocab_id'
        self.VOCAB_KEY = 'id'

    def flush(self):
        print("FLUSHING THE DATABASE MONGO COLLECTIONS")
        self.snippetsCollection.delete_many({})
        self.sampleCollection.delete_many({})
        self.vocabCollection.delete_many({})

    def existingSnippets(self):
        result = list(self.snippetsCollection.find({}, {self.SNIPPET_KEY: 1, '_id': 0}))
        values = [item[self.SNIPPET_KEY] for item in result]

        return values

    def getSnippets(self, snippets=None, limit=0):
        if snippets == None:
            snippets = self.existingSnippets()

        result = list(self.snippetsCollection.find({self.SNIPPET_KEY: {'$in': snippets}}, limit=limit))
        return result

    def existingSamples(self):
        result = list(self.sampleCollection.find({}, {self.SAMPLE_KEY: 1, '_id': 0}))
        values = [item[self.SAMPLE_KEY] for item in result]

        return values

    def getSample(self, sample=None, limit=0):
        if sample == None:
            sample = self.existingSample()

        result = list(self.sampleCollection.find({self.SAMPLE_KEY: {'$in': sample}}, limit=limit))
        return result

    def existingVocab(self):
        result = list(self.vocabCollection.find({}, {self.VOCAB_KEY: 1, '_id': 0}))
        values = [item[self.VOCAB_KEY] for item in result]

        return values

    def getVocab(self, vocab=None, limit=0):
        if vocab == None:
            vocab = self.existingVocab()

        result = list(self.vocabCollection.find({self.VOCAB_KEY: {'$in': vocab}}, limit=limit))
        return result

    def ingestItems(self, snippetItems, sampleItems):
        print(f"ingesting snippets: {len(snippetItems)} of snippets obj with type {type(snippetItems)}")
        # Process snippets
        self.snippetsCollection.insert_many(snippetItems.values())

        # Process samples
        self.sampleCollection.insert_many(sampleItems.values())

        # Build vocab
        existingVocab = set(self.existingVocab())

        # Update vocab
        for sample in sampleItems.values():
            if sample[self.SAMPLE_VOCAB_POINTER_KEY] not in existingVocab:
                self.vocabCollection.insert_one({
                    self.VOCAB_KEY: sample[self.SAMPLE_VOCAB_POINTER_KEY],
                    'lemma': sample['lemma'],
                    'pos': sample['pos'],
                    'word_freq': sample['word_freq'],
                    'rep_data': {
                        'last_review': None,
                        'next_review': str((datetime.now() + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)),
                        'current_interval': 1,
                        'ease': 2.5,
                        'quality': -1,
                        'history': [],
                    },
                    'tags': [],
                    'parents': [sample['parent_snippet']],
                    'samples': [sample[self.SAMPLE_KEY]]
                })

                existingVocab.add(sample[self.SAMPLE_VOCAB_POINTER_KEY])
            else:
                self.vocabCollection.update_one(
                    {self.VOCAB_KEY: sample[self.SAMPLE_VOCAB_POINTER_KEY]},
                    {
                        '$addToSet': {
                            'parents': sample['parent_snippet'],
                            'samples': sample[self.SAMPLE_KEY]
                        }
                    }
                )