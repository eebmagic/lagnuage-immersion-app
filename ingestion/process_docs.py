'''
Primary CLI interface for ingesting pdf documents from the source directory.
'''
import os
import json
import argparse
import pdfplumber
from tqdm import tqdm
import spacy

from clean import process_lines, split_sentences
from ingest import ingestNew

nlp = spacy.load('pt_core_news_sm')


parser = argparse.ArgumentParser(description='Process a directory of pdfs')
parser.add_argument(
    '--flush',
    action='store_true', help='Overwrite the existing entries in the database'
)
parser.add_argument(
    '--size',
    type=int,
    default=50,
    help='Size for chunks of entries to be processed at a time'
)
parser.add_argument(
    '--delay',
    type=float,
    default=0,
    help='Number of seconds to wait between chunks of entries'
)
parser.add_argument(
    '--pages',
    type=int,
    default=-1,
    help='Number of pages to ingest (default: -1 for all)'
)
args = parser.parse_args()

def pdf_to_text(pdf_path, meta, literal_page_nums=True, page_limit=None):
    '''
    Reads all the pdf pages in set set range
    and then generates snippets (with metadata) and page numbers.
    '''
    with pdfplumber.open(pdf_path) as pdf_plumb:
        print(f'Processing doc: {pdf_path}')
        print(f'  with {len(pdf_plumb.pages)} pages')

        start_page = meta.get('start_page', 1) - 1
        end_page = meta.get('end_page', float('inf')) - 1
        if page_limit and page_limit > 0:
            end_page = min(end_page, start_page + page_limit)

        # Get all the lines from all the pages
        processed_lines = []
        snippet_page_nums = []

        print('ITERATIVELY READING PAGES...')
        with tqdm(total=len(pdf_plumb.pages)) as pbar:
            for i, page in tqdm(enumerate(pdf_plumb.pages[:end_page])):
                if (i < start_page) or (i+1 > end_page):
                    pbar.update(1)
                    continue

                lines = page.extract_text_lines()
                processed, page_num = process_lines(lines)

                processed_lines.extend(processed)
                if literal_page_nums:
                    snippet_page_nums.extend([i+1] * len(processed))
                else:
                    snippet_page_nums.extend([page_num] * len(processed))

                pbar.update(1)

        return processed_lines, snippet_page_nums


if __name__ == '__main__':
    print('got args:')
    print(args)

    if args.flush:
        from CONFIG import PreferredInterface as Interface
        Interface.flush()

    # Find a pdf files
    SOURCE_PATH = './media/documents'
    pdfs = [f for f in os.listdir(SOURCE_PATH) if f.endswith('.pdf')]
    print(pdfs)


    with open('media/metadata.json', encoding='utf-8') as file:
        METADATA = json.load(file)
        print(f'Got metadata: {METADATA}')


    # Process Documents
    for pdf in pdfs:
        path = f'{SOURCE_PATH}/{pdf}'

        # Load text from file
        print(METADATA.keys(), pdf in METADATA.keys())
        doc_meta = METADATA[pdf]
        text_lines, page_nums = pdf_to_text(
            pdf_path=path,
            meta=doc_meta,
            page_limit=args.pages,
        )


        # Split the lines into sentences and page nums
        sents = split_sentences(text_lines, page_nums)

        # for sent in sents:
        #     print(f'\t{sent['id']}')
        #     print(f'\t{sent['page']}.{sent['page_sentence_index']}')
        #     print(f'\t{sent['text']}')
        #     print()
        print(f'\nFound {len(sents)} sentences in doc\n')


        # Check db for existing before processing
        ingestNew(
            sents,
            sourceType='pdf',
            sourcePath=path,
            chunkSize=args.size,
            chunkDelay=args.delay,
        )
