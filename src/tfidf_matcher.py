#!/usr/bin/env python2.7


import json
from stemming.porter2 import stem as stemmer
from multiprocessing import Pool
import os
import math
import re

FULL_PATH_DATA = '/Users/dima/Documents/cs224u_project/data'
INPUT_FILE = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_english.json')
STEM_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_total_counts_en.json')
REPRESENTATIVES = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_representatives_en.json')
INV_DOC_COUNTS = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_inv_doc_counts_en.json')
RESULT_FILE = os.path.join(FULL_PATH_DATA, 'bbc/bbc_april_total_tfidf_baseline_prediction.json')
OUT_INCORRECT = os.path.join(FULL_PATH_DATA, 'bbc/bbc_incorrect.json')


all_headlines = []
total_docs = 3546 #our corpus # docs length
inv = None


def make_stem_counts(text):
	C = {}
	for word in text.split():
		clean_word = re.sub(r'[^a-zA-Z ]','', word).lower()
		stem = stemmer(clean_word)
		C[stem] = C.get(stem, 0) + 1
	return C

def get_headlines(data):
	return [article['headline'] for article in data]


def assign_headline_tfidf_total(article):
	article_text = article["plaintext"]
	stem_counts = make_stem_counts(article_text)
	ranked_headlines = []
	for h in all_headlines:

		tfidf = 0
		for word in h.split():
			clean_word = re.sub(r'[^a-zA-Z ]','', word).lower()
			stem = stemmer(clean_word)
			stem_article_count = stem_counts.get(stem,0)
			if stem not in inv:
				continue
			if stem_article_count <= 0:
				continue
			stem_tfidf = math.log10(float(total_docs) / float(inv[stem])) * math.log10(stem_article_count)
			tfidf += stem_tfidf
		ranked_headlines += [(h, tfidf)]
	ranked_headlines.sort(key=lambda x: x[1], reverse=True)
	return (article, ranked_headlines[:20])



def main(data, total):
	global all_headlines
	global inv
	with open(INV_DOC_COUNTS) as inf:
		inv = json.load(inf)
	all_headlines = get_headlines(data)
	pool = Pool(1)
	counter = 0
	out_data = []
	for article, possible_headlines in pool.imap(assign_headline_tfidf_total, data):
		print counter, article["headline"]
		counter += 1
		article["tf_idf_prediction"] = possible_headlines
		out_data += [article]

	with open(RESULT_FILE,'w') as outf:
		json.dump(out_data, outf)

	num_correct = 0
	num_incorrect = 0
	incrt = []
	for article in out_data:
		if article["headline"] == article["tf_idf_prediction"][0][0]:
			num_correct += 1
		else:
			num_incorrect += 1
			incrt += [article]
	print "Num correct: %i" % num_correct
	print "Num incorrect: %i" % num_incorrect

	with open(OUT_INCORRECT,'w') as outf:
		json.dump(incrt, outf)


if __name__=="__main__":
	with open(INPUT_FILE) as inf:
		data = json.load(inf)
	with open(STEM_COUNTS) as inf:
		total = json.load(inf)




	main(data, total)