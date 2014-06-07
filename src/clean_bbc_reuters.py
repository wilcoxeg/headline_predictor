import os
import logging
import re
import sys
import json
import datetime
from urlparse import urlparse


FULL_PATH_DATA = '/Users/dima/Documents/cs224u_project/data'
INPUT_FILE = os.path.join(FULL_PATH_DATA, 'reuters/bbc_reuters_april.json')

def clean_plaintext(article):
	


def main(json_dict):
	for article in json_dict:
		plain = article['plaintext']
		clean_plain = clean_plaintext(plain)

if __name__=="__main__":
	import doctest
	doctest.testmod()
	with open(INPUT_FILE) as inf:
		data = json.load(inf)
	clean_data = main(data)