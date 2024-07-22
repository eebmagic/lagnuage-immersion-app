'''
A simple script that drops all mongo collections.
Usefule for when testing document ingestion and reseting user rep data.
'''
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')

client['language']['vocab'].drop()
client['language']['snippets'].drop()
client['language']['samples'].drop()

print('CLEARED COLLECTIONS')
