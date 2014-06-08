#!/usr/bin/env python2.7

import json
import os
import re
from stemming.porter2 import stem as stemmer
import sys
import re
from itertools import islice, izip
from collections import Counter

FULL_PATH_DATA = '/Users/dima/Documents/cs224u_project/data'
INPUT_FILE = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_english.json')
OUT_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_total_counts_en.json')
REPRESENTATIVES = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_representatives_en.json')
INV_DOC_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_inv_doc_counts_en.json')

def token_tfidf(in_doc_count, total_count, total_docs):
	

def update_progress(current, total):
	current += 1
	progress = int((current)*100/total)
	sys.stdout.write("\r[ %10s ] %d%% (%s/%s)" % ('#' * (progress / 10), progress, current, total))
	sys.stdout.flush()

def count(data):
	total_counts = {}
	stem_to_word = {} # stem to {word: count}
	for i, article in enumerate(data):
		update_progress(i, len(data))
		text = article.get('plaintext')
		for word in text.split():
			clean_word = re.sub(r'[^a-zA-Z ]','', word).lower()
			stem = stemmer(clean_word)
			cur_counts = stem_to_word.get(stem,{})
			cur_word_count = cur_counts.get(stem,0)
			cur_word_count += 1
			cur_counts[clean_word] = cur_word_count
			stem_to_word[stem] = cur_counts

			total_counts[stem] = total_counts.get(stem,0) + 1

	representative_tokens = {}
	for stem, counts in stem_to_word.iteritems():
		repr = max(counts, key=lambda x: counts[x])
		representative_tokens[stem] = repr

	with open(OUT_COUNTS, 'w') as outf:
		json.dump(total_counts, outf)
	with open(REPRESENTATIVES, 'w') as outf:
		json.dump(representative_tokens, outf)

def flush_dict(bigram_count, n_inclusive_below):
	keys_to_delete = [key for key in bigram_count if bigram_count[key] <= n_inclusive_below]
	for key in keys_to_delete:
		del bigram_count[key]
	return bigram_count

def find_bigrams(data):
	pass
	# total_bigram_counter = Counter()
	# for i, article in enumerate(data):
	# 	if i % 100 == 0:
	# 		bigram_count = flush_dict(bigram_count, 1)
	# 	update_progress(i, len(data))
	# 	text = article.get('plaintext')
	# 	words = re.findall("\w+", text)
	# 	total_bigram_counter.update(izip(words, islice(words, 1, None))))

def construct_inverse_document_matrix(data):
	stem_to_docs = {}
	for i, article in enumerate(data):
		update_progress(i, len(data))
		text = article.get('plaintext')
		for word in text.split():
			clean_word = re.sub(r'[^a-zA-Z ]','', word).lower()
			stem = stemmer(clean_word)
			cur_set = stem_to_docs.get(stem, set())
			cur_set.add(i)
			stem_to_docs[stem] = cur_set

	stem_to_doccount = {}
	for stem, docs in stem_to_docs.iteritems():
		stem_to_doccount[stem] = len(docs)

	with open(INV_DOC_COUNTS, 'w') as inf:
		json.dump(stem_to_doccount, inf)


def main(data):
	count(data)
	#find_bigrams(data)
	construct_inverse_document_matrix(data)

	# count(data)



if __name__=="__main__":
	with open(INPUT_FILE) as inf:
		data = json.load(inf)

	main(data)