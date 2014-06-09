import os

TOTAL_DOCS = 3546
FULL_PATH_DATA = '/Users/dima/Documents/cs224u_project/data'

# FILENAMES:
STEM_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_total_counts_en.json')
REPRESENTATIVES = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_representatives_en.json')
INV_DOC_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_inv_doc_counts_en.json')
TFIDF_PREDICTIONS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_total_tfidf_baseline_prediction.json')
ALL_HEADLINES_FILE = os.path.join(FULL_PATH_DATA, 'all_headlines.json')
INCORRECT_TFIDF = os.path.join(FULL_PATH_DATA, 'bbc/bbc_incorrect.json')