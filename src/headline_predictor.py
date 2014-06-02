#!/usr/bin/env python
import json
import math
import sys
import os
import nltk
import scipy
import numpy
import re
import Queue
from nltk.corpus import stopwords
import string

class News_Reader:

	def __init__(self):
		# The array of tuples where the headlines and articles are store
		self.stories = []
		# The array of tuples where the headliens are stored for testing.
		self.test_stories = [] 
		# The inverted index, where each word is mapped to the list of article it appears in.
		self.inv_index = {}
		# Keys are document numbers, values are touples of words and tfidf numbers for that doc.
		self.doc_tfidf = {}
		# Keys are document numbers, values are our candidate headlines (array of strings)
		self.headlines = {}
		self.seen_vocabulary = set()
		self.training_doc_tfidf = {}

		self.nouns_tags = ['NNP','NNPS','NNS']
		self.adj_tags = ['DC','JJ','JJR','JJS','RB','RBR','RBS']
		self.verb_tags = ['VB','VBD','VBG','VBN','VBP','VBZ']

	def clean_seperator(self, headline, seperator):
		"""
		if the news source is seperated by a dash, this cleans it.
		"""
		source_index = headline.find(seperator)
		if source_index != (-1):
			if source_index > (len(headline)/2):
				headline = headline[:source_index]
			else:
				headline = headline[source_index + 3:]
		return headline

	def clean_random(self, headline):
		"""
		This cleas various other bits from the headline: if it starts with a tab
		or if it is all question markes beacause of some foreign script.
		"""
		if headline[0] == '\t':
			headline = headline[1:]
		if headline[len(headline) - 1] == '\n':
			headline = headline[:len(headline) - 1]
		if '??' in headline: return None #Forieng language
		return headline

	def clean_headline(self, headline):
		"""
		Finds the start of the headline afte the url address
		And calls the individual functions to clean up the headline, so
		all we have is text, and no author or publication name.
		"""
		http_index = headline.find('http')
		headline_start_index = headline.find('	', http_index)
		headline = headline[headline_start_index:]
		headline = self.clean_seperator(headline, " | ")
		headline = self.clean_seperator(headline, " - ")
		headline = self.clean_seperator(headline, " : ")
		headline = self.clean_random(headline)
		return headline

	def clean_tags(self, article):
		"""
		This removes everything between a < and >, basically all html tags.
		"""
		while True:
			tag_start = article.find('<')
			if tag_start == (-1): break
			tag_end = article.find('>')
			if(tag_end < tag_start): break
			article = article[:tag_start] + article[tag_end + 1:]

		return article

	def clean_article(self, article):
		"""
		Replaces all the newline markers, which were used in article formatting,
		Also does not return an article if it has a bunch of ?s in it -- foreign language.
		"""
		article = article.replace('\\n', ' ')
		if "????" in article: return None #Foreign language
		article = self.clean_tags(article)
		article = nltk.word_tokenize(article)

		return article

	def get_articles(self, filename, training):
		"""
		Reads in three lines at a time (headline, article, then a bland third line).
		Calls functions to clean up the headline and article, and then stores both
		as a touple in the "stories" array.
		"""
		f = open(filename, 'r')
		while True:
			line1 = f.readline()
			line2 = f.readline()
			if not line2: break #EOF
			blankLine = f.readline() #blank line between articles

			line1 = self.clean_headline(line1)
			line2 = self.clean_article(line2)
			news_tuple = line1, line2

			if (line1 != None) and (line2 != None) and training:
				self.stories.append(news_tuple)
			if (line1 != None) and (line2 != None) and (not training):
				self.test_stories.append(news_tuple)



	def make_inv_index(self):
		"""
		For each document, splits each article into a set of words, and then adds the
		doc number to the set of docs that contain that word. Classic inverted index.
		"""
		inv_index = {}
		for d in range(len(self.stories)): #For each document
			for word in self.stories[d][1]:
				"""Add the word to the inverted index"""
				if word not in inv_index:
					inv_index[word] = set()
				inv_index[word].add(d)

				if word not in self.seen_vocabulary:
					self.seen_vocabulary.add(word)

		"""for each set, turn it into a list and sort the list"""
		for word in inv_index:
			inv_index[word] = list(inv_index[word])
			inv_index[word].sort()
		self.inv_index = inv_index

		#self.seen_vocabulary.add("UNK")




	def make_testing_tfidf_index(self):
		"""
		For each document, I get the frequency of each word, and generate a 
		tfidf score. I add the score to the "doc_tfidf" array, associated to its
		appropriate document.
		"""
		for d in range(len(self.test_stories)):
			words = {}
			"""collect the frequency of every word in the document"""
			for w in self.test_stories[d][1]:
				if w in words:
					words[w] += 1
				else:
					words[w] = 1

			"""for each word, add its tf.idf score"""
			for w in words:
				if w in self.seen_vocabulary:
					idf = float(float(len(self.stories)) / float(len(self.inv_index[w])))
					tfidf = (1 + math.log10(words[w])) * math.log10(idf)

				# The word must appear in more than 20 documents
				if (w in self.seen_vocabulary) and (len(self.inv_index[w]) > 2):

					if d not in self.doc_tfidf:
						self.doc_tfidf[d] = []
					word_tfidf_touple = tfidf, w
					self.doc_tfidf[d].append(word_tfidf_touple)


	def make_training_tfidf_index(self):
		"""
		For each document, I get the frequency of each word, and generate a 
		tfidf score. I add the score to the "doc_tfidf" array, associated to its
		appropriate document.
		"""
		for d in range(len(self.stories)):
			words = {}
			"""collect the frequency of every word in the document"""
			for w in self.stories[d][1]:
				if w in words:
					words[w] += 1
				else:
					words[w] = 1

			"""for each word, add its tf.idf score"""
			for w in words:
				idf = float(float(len(self.stories)) / float(len(self.inv_index[w])))
				tfidf = (1 + math.log10(words[w])) * math.log10(idf)

				# The word must appear in more than 2 documents
				#if (len(self.inv_index[w]) > 2):

				if d not in self.training_doc_tfidf:
					self.training_doc_tfidf[d] = {}
				self.training_doc_tfidf[d][w] = tfidf



	def get_average_headline_len(self):
		"""
		This calculates the average headline length. For the
		base model, we simply produce that many words for the
		headlines.
		"""
		average = 0
		for d in range(len(self.stories)):
			headline = self.stories[d][0].split(' ')
			length = len(headline)
			average += length
		average = (float(average) / float(len(self.stories)))
		return int(average)




	def predict_tfidf_headlines(self):
		"""
		This function populates the "headlines" array with the highest
		tfidf valued words for each headline.
		"""
		average_headline_length = self.get_average_headline_len()
		# For each document
		for d in range(len(self.test_stories)):
			self.doc_tfidf[d] = sorted(self.doc_tfidf[d], key=lambda tup: tup[0])
			if d not in self.headlines:
				self.headlines[d] = []
			# Add the average number of headline words into our candidate.
			for r in range(average_headline_length):
				# if there aren't enough possible headline words
				if ((len(self.doc_tfidf[d]) - r - 1) < 0): break
				self.headlines[d].append(self.doc_tfidf[d][len(self.doc_tfidf[d]) - r - 1])



	def bleu_score(self, candidate, reference):
		"""
		This impliments the BLEU algorithm, minus the brevity penalty.
		"""
		correct = 0
		for w in candidate:
			if w[1] in reference:
				correct += 1
		if(len(candidate)) > 0:
			return (float(correct) / float(len(candidate)))
		else: return 0

	def evaluate_headlines(self):
		"""
		This algorithm keeps track of the precision score for each document
		by calling the BLEU algorithm, it then calculates the mean precision
		and prints that to the user.
		"""
		self.precision_table = {}
		for d in range(len(self.test_stories)):
			# Our candidate headline (highest tfidf words for the article)
			candidate = self.headlines[d]
			# The actual headline.
			gold = self.test_stories[d][0]			

			if d not in self.precision_table:
				self.precision_table[d] = self.bleu_score(candidate, gold)
			print self.test_stories[d][0], " --- ", candidate, "precision: ", self.precision_table[d], '\n'

		# Calcuate the average precision.
		precision = 0
		for r in range(len(self.precision_table)):
			precision += self.precision_table[r]
		precision = float(precision) / float(len(self.precision_table))
		print "precision: ", precision

	def at_begining(self, word, doc_index):
		first_15 = self.stories[doc_index][:15]
		for elem in first_15:
			if elem == word:
				return 1.0
		return 0.0

	def train_classifier(self):
		for d in range(len(self.stories)):
			print "Adding: ", self.stories[d][0]
			tagged_story = nltk.pos_tag(self.stories[d][1])
			noun_list, verb_list, adj_list = [], [], []
			for word in tagged_story:
				if (word[1] in self.nouns_tags) and (word not in noun_list):
					noun_list.append(word[0])
				#if (word[1] in self.adj_tags): adj_list.append(word[0])
				#if (word[1] in self.verb_tags): verb_list.append(word[0])

			for w in noun_list:
				if (w in self.stories[d][0]):
					begning = self.at_begining(w, d)
					self.noun_training.append([{w: self.training_doc_tfidf[d][w], w: begining}, '1'])
				else: 
					self.noun_training.append([{w: self.training_doc_tfidf[d][w], w: self. at_begining(w, d)}, '0'])


			#adj_training.append(get_noun_features(document))
			#verb_training.append(get_verb_features(document))"""

		noun_feature_encoding = nltk.classify.maxent.TypedMaxentFeatureEncoding.train(self.noun_training)
		self.noun_classifier = nltk.MaxentClassifier.train(self.noun_training, algorithm='iis', encoding=noun_feature_encoding, max_iter=10)

	def get_tfidf(self, index, word):
		for elem in self.doc_tfidf[index]:
			if elem[1] == word:
				return elem[0]
		return 0

	def test_classifier(self):
		average_len = self.get_average_headline_len()
		for d in range(len(self.test_stories)):
			print "Testing: ", self.test_stories[d][0]
			tagged_story = nltk.pos_tag(self.test_stories[d][1])
			noun_list, verb_list, adj_list = [], [], []
			for word in tagged_story:
				if (word[1] in self.nouns_tags) and (word not in noun_list):
					noun_list.append(word[0])
				#if (word[1] in self.adj_tags): adj_list.append(word[0])
				#if (word[1] in self.verb_tags): verb_list.append(word[0])

			for word in noun_list:
				tfidf = self.get_tfidf(d, word)
				if self.noun_classifier.classify({word: tfidf, word: self.at_begining(word, d)}) == '1':
					self.headlines[d].append([0, word])
			self.headlines[d] = self.headlines[d][:average_len]

	def predict_learning_headlines(self):
		self.noun_classifier, self.verb_classifier, self.adj_classifier = None, None, None
		self.noun_training, self.adj_training, self.verb_training = [], [], []
		self.train_classifier()
		self.test_classifier()

	def clean_headlines(self):
		for d in range(len(self.headlines)):
			self.headlines[d] = []

def main(args):
	newser = News_Reader()
	train_number = 1
	#newser.get_articles("data/2014-04/2014040106_filtered")

	i = 0
	for filename in os.listdir('../data/2014-04/'):
		if ('meta' not in filename) and (i < train_number): #we don't care about the metadata
			print "train, ", filename
			newser.get_articles("../data/2014-04/" + filename, True)
		if ('meta' not in filename) and (i >= train_number) and (i < train_number + 1): #get one document for testing
			newser.get_articles("../data/2014-04/" + filename, False)
			print "test, ", filename

		i += 1

	newser.test_stories = newser.test_stories[3:18]
	newser.stories = newser.stories[50:100]
	print "Number of stories: ",len(newser.stories), " Number of tests: ", len(newser.test_stories)

	newser.make_inv_index()
	newser.make_testing_tfidf_index()
	newser.make_training_tfidf_index()

	newser.predict_tfidf_headlines()
	newser.evaluate_headlines()
	newser.clean_headlines()

	newser.predict_learning_headlines()
	newser.evaluate_headlines()
	newser.clean_headlines() 

if __name__ == '__main__':
	args = sys.argv[1:]
	main(args)