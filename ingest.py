import time
import math
import re

import wordfreq
import spacy
nlp = spacy.load('pt_core_news_sm')
from nltk.corpus import wordnet as wn

from CONFIG import PreferredTranslator as Translator
from CONFIG import PreferredInterface as Interface

WORD_FREQ_FILTER_THRESHOLD = 7.0


def lemmatize(text, parentSnippet=None):
    '''
    Default lemmatize function, using spacy.
    '''
    def realWord(text):
        # Check that a string isn't just punctuation
        return re.match(r'[^\w\s]', text) == None

    doc = nlp(text)
    result = {}
    seenLemmas = set()
    for i, word in enumerate(doc):
        lemma = word.lemma_
        freq = wordfreq.zipf_frequency(lemma, 'pt')

        if realWord(lemma) and lemma not in seenLemmas:
            seenLemmas.add(lemma)

            synsets = wn.synsets(lemma, lang='por')
            synValues = [(s.name(), s.definition()) for s in synsets]
            specificID =f"{lemma} - {word.pos_} - {i} - {parentSnippet}"

            # Filter to ignore super common words (the, a, of, etc.)
            if freq > WORD_FREQ_FILTER_THRESHOLD:
                continue

            m = {}
            m['text'] = word.text
            m['lemma'] = lemma
            m['pos'] = word.pos_
            m['synsets'] = synValues
            m['word_freq'] = freq
            m['sentence_order_position'] = i
            m['tags'] = []
            m['type'] = 'word'
            m['morph'] = word.morph.to_dict()
            m['head'] = word.head.text
            m['parent_snippet'] = parentSnippet
            m['generid_id'] = f"{lemma} - {word.pos_}"
            m['specific_id'] = specificID
            m['vect'] = word.vector.tolist()

            result[specificID] = m

    return result


def prepChunk(items, chunkString=''):
    # Pull text from items
    sents = [item['text'] for item in items]
    ids = [item['id'] for item in items]

    # Generate new data
    print(f"Getting translations for chunk: {chunkString}")

    try:
        sampleItemResults = {}
        lemmaSets = []
        for sent, idx in zip(sents, ids):
            lresult = lemmatize(sent, parentSnippet=idx)
            sampleItemResults.update(lresult)
            lemmaSets.append(list(lresult.keys()))
        translations = Translator.translate(sents)
    except Exception as e:
        print(f"Error prepping chunk: {e}")
        # Print full exception for debugging
        import traceback
        print(traceback.format_exc())
        print(f"Skipping chunk")
        raise e


    snippetResults = {}
    for item, translation, lemmaIds in zip(items, translations, lemmaSets):
        out = item.copy()
        out['trans'] = translation
        out['trans_model'] = Translator.metaName
        out['target_language'] = Translator.ogLanguage
        out['user_language'] = Translator.userLanguage

        out['contained_samples'] = lemmaIds
        snippetResults[out['id']] = out

    return snippetResults, sampleItemResults


def ingestAll(items, sourceType, sourcePath, chunkSize=10, chunkDelay=0):
    allSnippetItems = {}
    allSampleItems = {}
    totalChunks = math.ceil(len(items) / chunkSize)
    for i in range(0, len(items), chunkSize):
        chunk = items[i:i+chunkSize]
        chunkIndex = 1 + (i // chunkSize)
        try:
            snippetItems, sampleItems = prepChunk(chunk, chunkString=f"{chunkIndex} / {totalChunks}")
            for item in snippetItems.values():
                item['source_type'] = sourceType
                item['source_path'] = sourcePath
                allSnippetItems[item['id']] = item

            for item in sampleItems.values():
                allSampleItems[item['specific_id']] = item

            if chunkDelay:
                print(f"Sleeping for {chunkDelay} seconds...")
                time.sleep(chunkDelay)

        except KeyboardInterrupt:
            print(f"Caught KeyboardInterrupt, stopping ingestion")
            break

        except Exception as e:
            print(f"Error ingesting chunk {chunkIndex} - {totalChunks}: {e}")
            print(f"Skipping chunk")

    return allSnippetItems, allSampleItems


def ingestNew(
        items,
        sourceType,
        sourcePath,
        chunkSize=10,
        chunkDelay=0
    ):
    # Load existing entries
    existingEntries = Interface.existingSnippets()

    # Filter out existing entries
    newEntries = list(filter(lambda x: x['id'] not in existingEntries, items))
    print(f"Found {len(newEntries)} / {len(items)} to be new entries")

    # Ingest new entries
    if newEntries:
        snippetItems, sampleItems = ingestAll(newEntries, sourceType, sourcePath, chunkSize, chunkDelay)
        print(f"Ingesting {len(snippetItems)} snippets and {len(sampleItems)} sample items")
        Interface.ingestItems(snippetItems, sampleItems)
