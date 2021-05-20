import os
from arxivfilter import *

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(FILE_DIR, 'categories.txt'), 'r') as f:
    categories = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]

with open(os.path.join(FILE_DIR, 'keywords.txt'), 'r') as f:
    keywords = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]


af = ArxivFilter(categories=categories,
                 keywords=keywords)
af.run()



