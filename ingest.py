import time
import math
import re
import json
from tqdm import tqdm

import spacy
nlp = spacy.load('pt_core_news_sm')

from translators import HuggingFace as T
Translator = T()


def lemmatize(text):
    '''
    Default lemmatize function, using spacy.
    '''
    def realWord(text):
        # Check that a string isn't just punctuation
        return re.match(r'[^\w\s]', text) == None

    doc = nlp(text)
    lemmas = []
    for word in doc:
        lemma = word.lemma_
        if realWord(lemma) and lemma not in lemmas:
            lemmas.append(lemma.lower())

    return lemmas


def prepChunk(items, chunkString=''):
    # Pull text from items
    sents = [item['text'] for item in items]

    # Generate new data
    print(f"Getting translations for chunk: {chunkString}")

    try:
        lemmas = [lemmatize(item) for item in sents]
        translations = Translator.translate(sents)
    except Exception as e:
        print(f"Error processing chunk: {e}")
        # Print full exception for debugging
        import traceback
        print(traceback.format_exc())
        print(f"Skipping chunk")

    result = []
    for item, translation, lemma in zip(items, translations, lemmas):
        out = item.copy()
        out['trans'] = translation
        out['trans_model'] = Translator.metaName
        out['target_language'] = Translator.ogLanguage
        out['user_language'] = Translator.userLanguage
        out['lemmas'] = lemma
        result.append(out)
    
    return result


def ingestAll(items, sourceType, sourcePath, chunkSize=10, chunkDelay=0):
    result = {}
    totalChunks = math.ceil(len(items) / chunkSize)
    for i in range(0, len(items), chunkSize):
        chunk = items[i:i+chunkSize]
        chunkIndex = 1 + (i // chunkSize)
        try:
            preppedChunk = prepChunk(chunk, chunkString=f"{chunkIndex} / {totalChunks}")
            for item in preppedChunk:
                item['source_type'] = sourceType
                item['source_path'] = sourcePath
                result[item['id']] = item

            if chunkDelay:
                print(f"Sleeping for {chunkDelay} seconds...")
                time.sleep(chunkDelay)

        except KeyboardInterrupt:
            print(f"Caught KeyboardInterrupt, stopping ingestion")
            break

        except Exception as e:
            print(f"Error processing chunk {chunkIndex} - {totalChunks}: {e}")
            print(f"Skipping chunk")

    return result


def ingestNew(items, sourceType, sourcePath, entriesSource='./entries.json', chunkSize=10, chunkDelay=0):
    # Load existing entries
    with open(entriesSource) as file:
        existingEntries = json.load(file)
        print(f"Got {len(existingEntries)} existing entries")
    
    # Filter out existing entries
    newEntries = list(filter(lambda x: x['id'] not in existingEntries, items))
    print(f"Found {len(newEntries)} / {len(items)} to be new entries")

    # Ingest new entries
    processedResult = ingestAll(newEntries, sourceType, sourcePath, chunkSize, chunkDelay)

    # Update in file
    existingEntries.update(processedResult)
    with open(entriesSource, 'w') as file:
        json.dump(existingEntries, file)
        print(f"Updated entries file with {len(existingEntries)} total entries ({len(processedResult)} are new)")
