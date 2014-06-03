#!/usr/bin/env python2.7

import json
import nltk
from multiprocessing import Pool
import logging

DATASET = "april"
INPUT_JSON = "../data/raw/%s.json" % DATASET
OUTPUT_JSON_FILE = "../data/pos/%s.json" % DATASET
NUM_THREADS = 8

def pos_article(article):
	logging.info("%s - %s" % (article["date"], article["headline"]))
	plaintext = article["plaintext"]
	tokens = nltk.word_tokenize(plaintext)
	pos_tokens = nltk.pos_tag(tokens)
	article["pos"] = pos_tokens
	del article["plaintext"]
	return article



def main(input_json=INPUT_JSON, num_threads=NUM_THREADS, out_file=OUTPUT_JSON_FILE):
	with open(input_json) as in_j:
		data = json.load(in_j)

	pool = Pool(processes=NUM_THREADS)
	pos_result = pool.map(pos_article, data)
	logging.info("Writing...")
	with open(out_file,'w') as out:
		json.dump(pos_result, out)
	logging.info("Written to %s" % out_file)




if __name__=="__main__":
	logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
	main()