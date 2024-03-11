'''
This file are exchangable methods for dumping data somewhere.
Classes should be able to ingest a list of new samples and vocab items,
as well as return existing entrie ids.
'''

import json
import os
from abc import ABC, abstractmethod

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
        print("FLUSHING THE DATABASE")
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
