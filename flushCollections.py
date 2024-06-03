import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')

client['language']['vocab'].drop()
client['language']['snippets'].drop()
client['language']['samples'].drop()

print(f'CLEARED COLLECTIONS')

