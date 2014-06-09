#!/usr/bin/env python2.7

'''
This module takes in input articles and produces features. If it can it uses cached results of the features

'''

import nltk
from stemming.porter2 import stem as stemmer
from constants import FULL_PATH_DATA, TOTAL_DOCS, STEM_COUNTS, REPRESENTATIVES, INV_DOC_COUNTS, TFIDF_PREDICTIONS, ALL_HEADLINES_FILE, INCORRECT_TFIDF
import random
import json
import os
import math
from copy import deepcopy

inv = {} # see main
FEATURES = []
TRAINING_VECTORS = os.path.join(FULL_PATH_DATA, 'bbc/training_vectors.json')

def _pos_tag(sentence):
	tokenized = nltk.word_tokenize(sentence.lower())
	return nltk.pos_tag(tokenized)



def feature_is_top_tfidf(article, headline, compute_if_not_cached=False):
	''' if cached, return true. if not cached, compute the tfidf and see if it falls into the range (optionally)'''
	headlines = article["tf_idf_prediction"]
	top_headline = headlines[0][0] == headline
	if top_headline:
		return 1
	else:
		if not compute_if_not_cached:
			return 0
		else:
			print "HAVE TO IMPLEMENT TF-IDF in feature_extract.py"
			raise Exception("HAVE TO IMPLEMENT TF-IDF in feature_extract.py")


def feature_is_top_five_tfidf(article, headline, compute_if_not_cached=False):
	headlines = article["tf_idf_prediction"]
	top_five = [h[0] for h in headlines[:5]]

	if headline in top_five:
		return 1
	else:
		return 0

def feature_is_top_twenty(article, headline, compute_if_not_cached=False):
	headlines = article["tf_idf_prediction"]
	top_twenty = [h[0] for h in headlines[:20]]

	if headline in top_twenty:
		return 1
	else:
		return 0

def _stem_idf(stem):
	if inv.get(stem,None):
		return math.log10(float(TOTAL_DOCS) / float(inv[stem]))
	else:
		return 0

def feature_is_idf_noun(article, headline):
	''' 
	Feature equals the sentence number from start in which the noun (top two headline nouns are taken with rank of idf) overlaps (subject).
	If no overlap then the feature is set to 0. If overlap then yes. 
	'''
	headline_pos = _pos_tag(headline.lower())
	nouns = [w for w,n in headline_pos if n[0]=='N']
	noun_stems = [stemmer(n) for n in nouns]
	best_nouns = sorted(noun_stems, key=lambda stem: _stem_idf(stem), reverse=True)
	text = article["plaintext"]
	first_sentences = text.split('.')[:3]
	for noun in best_nouns[:2]:
		for i, sentence in enumerate(first_sentences):
			s_l = sentence.lower()
			stems = [stemmer(word) for word in s_l.split()]
			if noun in stems:
				return i+1
	return 0




def feature_is_first_noun(article, headline):
	'''
	Returns sentence in which first noun of the headline appears in
	'''
	if not headline:
		import pdb; pdb.set_trace()
	print headline
	headline_pos = _pos_tag(headline.lower())
	nouns = [w for w,n in headline_pos if n[0]=='N']
	noun_stems = [stemmer(n) for n in nouns]
	text = article["plaintext"]
	first_sentences = text.split('.')[:3]
	if len(noun_stems) == 0:
		return 0
	first_stem = noun_stems[0]

	for i, sentence in enumerate(first_sentences):
		s_l = sentence.lower()
		stems = [stemmer(word) for word in s_l.split()]
		if first_stem in stems:
			return i + 1
	return 0


def feature_is_idf_verb(article, headline):
	headline_pos = _pos_tag(headline.lower())
	verbs = [w for w,n in headline_pos if n[0]=='V']
	verb_stems = [stemmer(n) for n in verbs]
	best_verbs = sorted(verb_stems, key=lambda stem: _stem_idf(stem), reverse=True)
	text = article["plaintext"]
	first_sentences = text.split('.')[:3]
	for verb in best_verbs[:2]:
		for i, sentence in enumerate(first_sentences):
			s_l = sentence.lower()
			stems = [stemmer(word) for word in s_l.split()]
			if verb in stems:
				return i + 1
	return 0



def feature_is_first_verb(article, headline):
	headline_pos = _pos_tag(headline.lower())
	verbs = [w for w,n in headline_pos if n[0]=='V']
	verb_stems = [stemmer(n) for n in verbs]
	if len(verb_stems) == 0:
		return 0
	first_verb = verb_stems[0]
	text = article["plaintext"]
	first_sentences = text.split('.')[:3]
	for i, sentence in enumerate(first_sentences):
		s_l = sentence.lower()
		stems = [stemmer(word) for word in s_l.split()]
		if first_verb in stems:
			return i + 1
	return 0

def construct_training_correct(data):
	training_list = []
	for article in data:
		signature = _get_feature_vector(article, article["headline"])
		article["feature_signature"] = signature
		article["output"] = 1
		training_list += [deepcopy(article)]
	print len(training_list)
	return training_list

def _select_incorrect(article):
	hs = article["tf_idf_prediction"]
	h = random.sample(hs,1)[0][0]
	while h == article["headline"]:
		h = random.sample(hs,1)[0][0] # change to something not correct
	return h


def construct_training_incorrect(data):
	output_list = []
	for article in data:
		h = _select_incorrect(article)
		signature = _get_feature_vector(article,h)
		output = 0
		article["feature_signature"] = signature
		article["output"] = output
		output_list += [deepcopy(article)]
	print len(output_list)
	return output_list

def _get_feature_vector(article, h):
	signature = []
	for f in FEATURES:
		signature += [f(article, h)]
	return signature

def construct_close_incorrect(incorrect_tfidf):
	output_list = []
	for i, article in enumerate(incorrect_tfidf):

		# half the time, choose the top (incorrect article)
		if i % 2 == 0:
			# choose the top article
			h = article["tf_idf_prediction"][0][0]
			output = 0
			signature = _get_feature_vector(article, h)
			article["feature_signature"] = signature
			article["output"] = output
			output_list += [article]
		else:
			# choose top-5 tfidf headline (might be correct -- dup of data)
			h = random.sample(article["tf_idf_prediction"][:5], 1)[0][0]
			output = 1 if h == article["headline"] else 0
			signature = _get_feature_vector(article, h)
			article["feature_signature"] = signature
			article["output"] = output
			output_list += [article]

	print len(output_list)
	return output_list


def main():
	global inv
	global FEATURES

	FEATURES = [feature_is_top_tfidf, feature_is_top_five_tfidf, feature_is_top_twenty, feature_is_first_noun, feature_is_first_verb, feature_is_idf_noun, feature_is_idf_verb]

	with open(INV_DOC_COUNTS) as inf:
		inv = json.load(inf)
	with open(TFIDF_PREDICTIONS) as inf:
		data = json.load(inf)
	with open(INCORRECT_TFIDF) as inf:
		incorrect_tfidf = json.load(inf)
	print len(data)
	training = []; test = []
	random.seed(0)
	print 'training +'
	training += construct_training_correct(data[:2000])
	print 'trining -'
	training += construct_training_incorrect(data[2000:3000])
	print 'trianing +/-'
	training += construct_close_incorrect(incorrect_tfidf[-1000:])

	with open(TRAINING_VECTORS, 'w') as outf:
		json.dump(training, outf)
	print 'dumped to %s' % TRAINING_VECTORS

if __name__=="__main__":
	main()

