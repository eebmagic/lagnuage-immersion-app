import time
import math
import re
import json
from tqdm import tqdm

import wordfreq
import spacy
nlp = spacy.load('pt_core_news_sm')
from nltk.corpus import wordnet as wn

from translators import HuggingFace as T
Translator = T()


def lemmatize(text, parentSnippet=None):
    '''
    Default lemmatize function, using spacy.
    '''
    def realWord(text):
        # Check that a string isn't just punctuation
        return re.match(r'[^\w\s]', text) == None

    doc = nlp(text)
    lemmas = []
    ids = []
    for word in doc:
        lemma = word.lemma_
        if realWord(lemma) and lemma not in lemmas:
            synsets = wn.synsets(lemma, lang='por')
            synValues = [(s.name(), s.definition()) for s in synsets]
            specificID =f"{lemma} - {word.pos_} - {parentSnippet}"

            m = {}
            m['text'] = word.text
            m['lemma'] = lemma
            m['pos'] = word.pos_
            m['synsets'] = synValues
            m['word_freq'] = wordfreq.zipf_frequency(lemma, 'pt')
            m['tags'] = []
            m['type'] = 'word'
            m['morph'] = word.morph.to_dict()
            m['head'] = word.head.text
            m['parent_snippet'] = parentSnippet
            m['generid_id'] = f"{lemma} - {word.pos_}"
            m['specific_id'] = specificID
            # m['vect'] = word.vector.tolist()

            print(json.dumps(m, indent=2))

            lemmas.append(m)
            ids.append(specificID)

    return lemmas, ids


def prepChunk(items, chunkString=''):
    # Pull text from items
    sents = [item['text'] for item in items]
    ids = [item['id'] for item in items]

    # Generate new data
    print(f"Getting translations for chunk: {chunkString}")

    try:
        lemmas = [lemmatize(sent, parentSnippet=idx) for sent, idx in zip(sents, ids)]
        translations = Translator.translate(sents)
    except Exception as e:
        print(f"Error processing chunk: {e}")
        # Print full exception for debugging
        import traceback
        print(traceback.format_exc())
        print(f"Skipping chunk")

    snippetResults = []
    vocabItemResults = []
    for item, translation, lemma in zip(items, translations, lemmas):
        out = item.copy()
        out['trans'] = translation
        out['trans_model'] = Translator.metaName
        out['target_language'] = Translator.ogLanguage
        out['user_language'] = Translator.userLanguage

        lemmaItems, lemmaIDs = lemma
        out['lemmas'] = lemmaIDs
        snippetResults.append(out)
        vocabItemResults.extend(lemmaItems)
    
    print(json.dumps(snippetResults, indent=2))
    quit()

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
