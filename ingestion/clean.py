import re
from nltk.tokenize import sent_tokenize
from hashlib import sha256

def check_line(line):
    '''
    check with regex if line is just a page number
    '''
    result = re.match(r'^(page |pg )?\d+$', line)
    return result == None


def clean(line):
    if line.startswith('- '):
        line = line[2:]

    return line

def process_lines(lines):
    out = []
    N = 3
    pageNum = None
    for i, line in enumerate(lines):
        line = line['text']
        if i < N or i > len(lines) - N:
            if check_line(line):
                out.append(line)
            else:
                pageNum = line.strip()

        else:
            out.append(line)

    cleaned = list(map(clean, out))

    return cleaned, pageNum


def split_sentences(lines, numbers):
    def getMostFreq(nums):
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
        else:
            return '-1'


    out = []
    buffer = ""
    numBuffer = []
    pageSentCounts = {}
    sentenceCounter = 0
    for line, num in zip(lines, numbers):
        buffer = (buffer + ' ' + line).strip()
        numBuffer.append(num)
        sents = sent_tokenize(buffer, language='portuguese')
        if len(sents) > 1:
            for sent in sents[:-1]:
                properPage = getMostFreq(numBuffer)
                pageCount = pageSentCounts.get(properPage, 0)
                pageSentCounts[properPage] = pageCount + 1
                out.append({
                    'id': sha256(sent.encode('utf-8')).hexdigest(),
                    'page': properPage,
                    'page_sentence_index': pageCount,
                    'combined_index': f'{properPage}.{pageCount}',
                    'media_index': sentenceCounter,
                    'text': sent,
                })
                sentenceCounter += 1
            buffer = sents[-1]
            numBuffer = [numBuffer[-1]]

    # TODO: Having this extra iteration outside the loop is a STRONG code smell.
    # Get the last sentence from leftover buffers
    properPage = getMostFreq(numBuffer)
    pageCount = pageSentCounts.get(properPage, 0)
    pageSentCounts[properPage] = pageCount + 1
    out.append({
        'id': sha256(buffer.encode('utf-8')).hexdigest(),
        'page': getMostFreq(numBuffer),
        'page_sentence_index': pageCount,
        'combined_index': f'{properPage}.{pageCount}',
        'media_index': sentenceCounter,
        'text': buffer,
    })

    return out