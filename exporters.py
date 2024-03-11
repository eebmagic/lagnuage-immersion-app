'''
This file are exchangable methods for dumping data somewhere.
Classes should be able to ingest a list of new samples and vocab items,
as well as return existing entrie ids.
'''

import json
import os
from abc import ABC, abstractmethod
import pymongo

class BaseExporter(ABC):
    '''
    This class is used to check that all exporters have the required methods.
    '''
    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def existingSamples(self):
        pass

    @abstractmethod
    def getSamples(self, samples=None):
        pass

    @abstractmethod
    def existingVocab(self):
        pass

    @abstractmethod
    def getVocab(self, vocab=None):
        pass

    @abstractmethod
    def ingestItems(self, sampleItems, vocabItems):
        pass


class LocalFiles(BaseExporter):
    def __init__(self, samplesPath='./entries/entries.json', vocabPath='./entries/vocab.json'):
        self.samplesPath = samplesPath
        self.vocabPath = vocabPath

        # Check file exists and is not empty
        if not os.path.exists(samplesPath) or os.path.getsize(samplesPath) == 0:
            print(f"Creating new entries file at {samplesPath}")
            with open(samplesPath, 'w') as file:
                file.write('{}')

        if not os.path.exists(vocabPath) or os.path.getsize(vocabPath) == 0:
            with open(vocabPath, 'w') as file:
                file.write('{}')

    def flush(self):
        print("FLUSHING THE DATABASE LOCAL FILE")
        with open(self.samplesPath, 'w') as file:
            file.write('{}')

        with open(self.vocabPath, 'w') as file:
            file.write('{}')

    # Handle sample items
    def existingSamples(self):
        with open(self.samplesPath) as file:
            existingEntries = json.load(file)
            return set(existingEntries.keys())

    def getSamples(self, samples=None):
        if samples == None:
            samples = self.existingSamples()

        with open(self.samplesPath) as file:
            existingEntries = json.load(file)
            return [existingEntries[idx] for idx in samples]

    # Handle vocab items
    def existingVocab(self):
        with open(self.vocabPath) as file:
            existingVocab = json.load(file)
            return set(existingVocab.keys())

    def getVocab(self, vocab=None):
        if vocab == None:
            vocab = self.existingVocab()

        with open(self.vocabPath) as file:
            existingVocab = json.load(file)
            return [existingVocab[idx] for idx in vocab]

    # Handle new items
    def ingestItems(self, sampleItems, vocabItems):
        '''
        This func assumes that the provided items are new to the collections
        '''
        # Process samples
        with open(self.samplesPath) as file:
            existingEntries = json.load(file)

        existingEntries.update(sampleItems)

        with open(self.samplesPath, 'w') as file:
            json.dump(existingEntries, file)

        # Process vocab
        with open(self.vocabPath) as file:
            existingVocab = json.load(file)

        existingVocab.update(vocabItems)

        with open(self.vocabPath, 'w') as file:
            json.dump(existingVocab, file)


class MongoExporter(BaseExporter):
    def __init__(self, mongoURI):
        self.mongoURI = mongoURI
        self.client = pymongo.MongoClient(mongoURI)

        # TODO: Check if collections and db exist

        self.db = self.client['language']
        self.samplesCollection = self.db['samples']
        self.vocabCollection = self.db['vocab']

        self.SAMPLE_KEY = 'id'
        self.VOCAB_KEY = 'specific_id'

    def flush(self):
        print("FLUSHING THE DATABASE MONGO COLLECTIONS")
        self.samplesCollection.delete_many({})
        self.vocabCollection.delete_many({})

    def existingSamples(self):
        result = list(self.samplesCollection.find({}, {self.SAMPLE_KEY: 1, '_id': 0}))
        values = [item[self.SAMPLE_KEY] for item in result]

        return values

    def getSamples(self, samples=None, limit=0):
        if samples == None:
            samples = self.existingSamples()

        result = list(self.samplesCollection.find({self.SAMPLE_KEY: {'$in': samples}}, limit=limit))
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

    def ingestItems(self, sampleItems, vocabItems):
        print(f"ingesting samples: {len(sampleItems)} of samples obj with type {type(sampleItems)}")
        # Process samples
        self.samplesCollection.insert_many(sampleItems.values())

        # Process vocab
        self.vocabCollection.insert_many(vocabItems.values())
