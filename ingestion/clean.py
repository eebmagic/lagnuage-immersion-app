'''
Collection of helper functions to help with prepping text for translation.
'''
import re
from hashlib import sha256
from nltk.tokenize import sent_tokenize

def check_line(line):
    '''
    check with regex if line is just a page number
    '''
    result = re.match(r'^(page |pg )?\d+$', line)
    return result is None


def clean(line):
    '''
    remove leading symbol from line
    '''
    if line.startswith('- '):
        line = line[2:]

    return line

def process_lines(lines):
    '''
    Get the cleaned lines of text and page number for a page.
    '''
    out = []
    n = 3
    page_num = None
    for i, line in enumerate(lines):
        line = line['text']
        if i < n or i > len(lines) - n:
            if check_line(line):
                out.append(line)
            else:
                page_num = line.strip()

        else:
            out.append(line)

    cleaned = list(map(clean, out))

    return cleaned, page_num


def split_sentences(lines, numbers):
    '''
    Split lines of text from pdf to sentences.
    Generates indexing data in the process.
    '''
    def get_most_freq(nums):
        counts = {}
        for num in nums:
            if num not in counts:
                counts[num] = 0
            counts[num] += 1

        maxval = max(counts.values())
        for key, val in counts.items():
            if val == maxval:
                return key

        if nums[0]:
            return nums[0]

        return '-1'

    out = []
    buffer = ""
    num_buffer = []
    page_sent_counts = {}
    sentence_counter = 0
    for line, num in zip(lines, numbers):
        buffer = (buffer + ' ' + line).strip()
        num_buffer.append(num)
        sents = sent_tokenize(buffer, language='portuguese')
        if len(sents) > 1:
            for sent in sents[:-1]:
                proper_page = get_most_freq(num_buffer)
                page_count = page_sent_counts.get(proper_page, 0)
                page_sent_counts[proper_page] = page_count + 1
                out.append({
                    'id': sha256(sent.encode('utf-8')).hexdigest(),
                    'page': proper_page,
                    'page_sentence_index': page_count,
                    'combined_index': f'{proper_page}.{page_count}',
                    'media_index': sentence_counter,
                    'text': sent,
                })
                sentence_counter += 1
            buffer = sents[-1]
            num_buffer = [num_buffer[-1]]

    # TODO: Having this extra iteration outside the loop is a STRONG code smell.
    # Get the last sentence from leftover buffers
    proper_page = get_most_freq(num_buffer)
    page_count = page_sent_counts.get(proper_page, 0)
    page_sent_counts[proper_page] = page_count + 1
    out.append({
        'id': sha256(buffer.encode('utf-8')).hexdigest(),
        'page': get_most_freq(num_buffer),
        'page_sentence_index': page_count,
        'combined_index': f'{proper_page}.{page_count}',
        'media_index': sentence_counter,
        'text': buffer,
    })

    return out
