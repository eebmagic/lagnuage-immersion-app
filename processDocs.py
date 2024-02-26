import os
import json
import pdfplumber
from tqdm import tqdm
import argparse

import spacy
nlp = spacy.load('pt_core_news_sm')

from clean import process_lines, split_sentences
# from ingest import ingestAll

parser = argparse.ArgumentParser(description='Process a directory of pdfs')
parser.add_argument('--flush', action='store_true', help='Overwrite the existing entries in the database')
parser.add_argument('--size', type=int, default=50, help='Size for chunks of entries to be processed at a time')
parser.add_argument('--delay', type=int, default=0, help='Number of seconds to wait between chunks of entries')
args = parser.parse_args()

def pdf_to_text(pdfPath, meta, literal_page_nums=True):
    with pdfplumber.open(pdfPath) as pdf:
        print(f"Processing doc: {pdfPath}")
        print(f"  with {len(pdf.pages)} pages")

        start_page = meta.get('start_page', 1) - 1
        end_page = meta.get('end_page', float('inf')) - 1

        # Get all the lines from all the pages
        textLines = []
        pageNums = []
        
        print(f"ITERATIVELY READING PAGES...")
        with tqdm(total=len(pdf.pages)) as pbar:
            for i, page in tqdm(enumerate(pdf.pages)):
                if (i < start_page) or (i+1 > end_page):
                    pbar.update(1)
                    continue

                lines = page.extract_text_lines()
                processed, pageNum = process_lines(lines)

                textLines.extend(processed)
                if literal_page_nums:
                    pageNums.extend([i+1] * len(processed))
                else:
                    pageNums.extend([pageNum] * len(processed))

                pbar.update(1)

        return textLines, pageNums


if __name__ == '__main__':
    print(f"got args:")
    print(args)

    if args.flush:
        print("FLUSHING THE DATABASE")
        with open('./entries.json', 'w') as file:
            file.write('{}')

    # Find a pdf files
    SOURCE_PATH = './media/documents'
    pdfs = [f for f in os.listdir(SOURCE_PATH) if f.endswith('.pdf')]
    print(pdfs)

    # Load existing entries
    with open('entries.json') as file:
        ENTRIES = json.load(file)
        print(f"Got entries: {ENTRIES}")

    with open('media/metadata.json') as file:
        METADATA = json.load(file)
        print(f"Got metadata: {METADATA}")


    # Process Documents
    for pdf in pdfs:
        pdfPath = f"{SOURCE_PATH}/{pdf}"

        # Load text from file
        print(METADATA.keys(), pdf in METADATA.keys())
        doc_meta = METADATA[pdf]
        text_lines, page_nums = pdf_to_text(pdfPath, doc_meta)
        
        print(text_lines[:5])
        print(page_nums[:5])


        # Split the lines into sentences and page nums
        sents = split_sentences(text_lines, page_nums)

        print('\nGOT THESE SENTENCES FROM PAGE 45:')
        for sent in sents[-100:]:
            print(f"\t{sent['id']}")
            print(f"\t{sent['page']}.{sent['sentence_index']}")
            print(f"\t{sent['text']}")
            print()
        print(f"Found {len(sents)} sentences in doc")
        

        # # Check db for existing before processing
        # newEntries = list(filter(lambda x: x['id'] not in ENTRIES, sents))
        # print(f"Found {len(newEntries)} / {len(sents)} to be new entries")
        # newEntries = newEntries[:3]
        # prepped = ingestAll(newEntries)
        # print(json.dumps(prepped[-1], indent=2))
        # print(prepped[-1]['text'])
