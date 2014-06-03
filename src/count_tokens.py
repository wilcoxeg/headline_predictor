#!/usr/bin/env python2.7

import os
import logging
import re
import sys
import json
import datetime
from urlparse import urlparse


OUTFILE = '../data/counted/raw_april.json'
IN_DIR = '../data/raw_april/'
TAG_REGEX = re.compile(r'<.*?>')
VALID_TLDS = [".com", ".co.uk"]
# GLOBAL_COUNTS = '../data/counted/global_counts.json'


def itersplit(s, sep=None):
    exp = re.compile(r'\s+' if sep is None else re.escape(sep))
    pos = 0
    while True:
        m = exp.search(s, pos)
        if not m:
            if pos < len(s) or sep is not None:
                yield s[pos:]
            break
        if pos < m.start() or sep is not None:
            yield s[pos:m.start()]
        pos = m.end()

def get_articles(filename):
	stories = []
	with open(filename, 'r') as f:	
		while True:
			line1 = f.readline()
			line2 = f.readline()
			if not line2: break #EOF
			blankLine = f.readline() #blank line between articles

			headline = clean_headline(line1)
			text = clean_article(line2)
			date_str = clean_date(line1)
			publisher = clean_publisher(line1)
			url = clean_url(line1)

			if headline and text and date_str:
				news_tuple = {"headline": headline, "plaintext": text, "date": date_str, "publisher": publisher, "url": url}
				logging.debug('About to yield %s' % str(news_tuple))
				yield news_tuple


def clean_random(headline):
	"""
	This cleas various other bits from the headline: if it starts with a tab
	or if it is all question markes beacause of some foreign script.
	"""
	if '??' in headline: return None #Forieng language
	return headline

def clean_date(headline_text):
	"""
	>>> clean_date('2014040106250000001    201404010625    http://www.forbes.com/sites/gregcaressi/2014/04/01/the-boom-continues-dissecting-himss14/    The Boom Continues : Dissecting HIMSS14 - Forbes')
	'2014/04/01'
	>>> clean_date('2014040106510000003    20140401065    http://www.wcvb.com/entertainment/quilt-exhibit-showcases-beauty-at-museum-of-fine-arts/25257670    Quilt exhibit showcases beauty at Museum of Fine Arts | Entertainment - WCVB Home')
	'2014/04/01'
	"""


	headline_els_t = headline_text.split('\t')
	headline_els_s = headline_text.split('    ')
	headline_els = max(headline_els_s, headline_els_t, key=lambda x: len(x))
	
	try:
		datestr = headline_els[1]
		date_obj = datetime.datetime.strptime(datestr, "%Y%m%d%H%M")
		return date_obj.strftime("%Y/%m/%d")
	except IndexError:
		logging.error('Could not parse the headline: %s' % headline_text)
		logging.error('Current parse: %s' % str(headline_els))
		return datestr

def clean_url(headline_text):
	"""
	>>> clean_url('2014040106250000001    201404010625    http://www.forbes.com/sites/gregcaressi/2014/04/01/the-boom-continues-dissecting-himss14/    The Boom Continues : Dissecting HIMSS14 - Forbes')
	'http://www.forbes.com/sites/gregcaressi/2014/04/01/the-boom-continues-dissecting-himss14/'
	"""
	headline_els_t = headline_text.split('\t')
	headline_els_s = headline_text.split('    ')
	headline_els = max(headline_els_s, headline_els_t, key=lambda x: len(x))

	try:
		return headline_els[2]

	except IndexError:
		logging.error('Could not parse the headline: %s' % headline_text)
		logging.error('Current parse: %s' % str(headline_els))
		return ''

def clean_publisher(headline_text):
	"""
	>>> clean_publisher('2014040106250000001    201404010625    http://www.forbes.com/sites/gregcaressi/2014/04/01/the-boom-continues-dissecting-himss14/    The Boom Continues : Dissecting HIMSS14 - Forbes')
	'forbes'
	>>> clean_publisher('2014040106510000003    20140401065    http://www.wcvb.com/entertainment/quilt-exhibit-showcases-beauty-at-museum-of-fine-arts/25257670    Quilt exhibit showcases beauty at Museum of Fine Arts | Entertainment - WCVB Home')
	'wcvb'
	>>> clean_publisher('2014040106470000003    201404010647    http://news.yahoo.com/japan-relaxes-arms-export-regime-fortify-defense-022501642--sector.html    Japan relaxes arms export regime to fortify defense - Yahoo News')
	'yahoo'
	>>> clean_publisher('2014040106470000003    201404010647    http://news.long_domain.co.uk/japan-relaxes-arms-export-regime-fortify-defense-022501642--sector.html    Japan relaxes arms export regime to fortify defense - Yahoo News')
	'long_domain'
	>>> clean_publisher('2014040106470000003    201404010647    http://www.feeds.reuters.com/japan-relaxes-arms-export-regime-fortify-defense-022501642--sector.html    Japan relaxes arms export regime to fortify defense - Yahoo News')
	'reuters'
	>>> clean_publisher('2014040106470000003    201404010647    http://news.foreign_domain.cn/japan-relaxes-arms-export-regime-fortify-defense-022501642--sector.html    Japan relaxes arms export regime to fortify defense - Yahoo News')
	'news.foreign_domain.cn'
	"""
	headline_els_t = headline_text.split('\t')
	headline_els_s = headline_text.split('    ')
	headline_els = max(headline_els_s, headline_els_t, key=lambda x: len(x))

	try:
		url = headline_els[2]
		parsed_uri = urlparse( url )
		loc = parsed_uri.netloc
		for tld in VALID_TLDS:
			tld_loc = loc.rfind(tld)
			if tld_loc > 0:
				without_tld = loc[:tld_loc]
				period_loc = without_tld.rfind('.')
				loc = without_tld[period_loc+1:]
				break
		return loc



	except IndexError:
		logging.error('Could not parse the headline: %s' % headline_text)
		logging.error('Current parse: %s' % str(headline_els))
		return ''

def clean_headline(headline_text):
	"""
	>>> clean_headline('2014040106250000001    201404010625    http://www.forbes.com/sites/gregcaressi/2014/04/01/the-boom-continues-dissecting-himss14/    The Boom Continues : Dissecting HIMSS14 - Forbes')
	'The Boom Continues : Dissecting HIMSS14'
	>>> clean_headline('2014040106510000003    20140401065    http://www.wcvb.com/entertainment/quilt-exhibit-showcases-beauty-at-museum-of-fine-arts/25257670    Quilt exhibit showcases beauty at Museum of Fine Arts | Entertainment - WCVB Home')
	'Quilt exhibit showcases beauty at Museum of Fine Arts'
	>>> clean_headline('2014040106470000003    201404010647    http://news.yahoo.com/japan-relaxes-arms-export-regime-fortify-defense-022501642--sector.html    Japan relaxes arms export regime to fortify defense - Yahoo News')
	'Japan relaxes arms export regime to fortify defense'
	"""
	headline_els_t = headline_text.split('\t')
	headline_els_s = headline_text.split('    ')
	headline_els = max(headline_els_s, headline_els_t, key=lambda x: len(x))

	headline = ''
	try:
		headline = headline_els[3]
	except IndexError:
		logging.error('Could not parse the headline: %s' % headline_text)
		logging.error('Current parse: %s' % str(headline_els))
		return headline

	for separator in ['|', '-']:
		headline = max(headline.split(separator), key=lambda x: len(x.split())) # keep the subtitle with the most words

	# things that sometimes are needed
	# for separator in [':']:
	# 	sep_els = headline.partition(separator)
	# 	useful = [el for el in sep_els if len(el.split()) > 1] # colon should separate out useful words
	# 	" ".join(useful)
	headline = clean_random(headline)
	if headline:
		return headline.strip()
	else:
		return None


def clean_tags(article):
	"""
	This removes everything between a < and >, basically all html tags.
	"""

	return TAG_REGEX.sub('', article)
	# while True:
	# 	tag_start = article.find('<')
	# 	if tag_start == (-1): break
	# 	tag_end = article.find('>')
	# 	if(tag_end < tag_start): break
	# 	article = article[:tag_start] + article[tag_end + 1:]
	# return article

def clean_article(article):
	if not article:
		return None
	article = article.replace('\\n', ' ')
	if "????" in article: return None #Foreign language
	article = clean_tags(article)
	try:
		article_new = re.sub(r'[^,.a-zA-Z0-9 ]','', article)
		article = article_new
	except:
		import pdb; pdb.set_trace()
	return article

def update_progress(progress, current, total):
	progress = int(progress)
	sys.stdout.write("\r[ %10s ] %d%% (%s/%s)" % ('#' * (progress / 10), progress, current, total))
	sys.stdout.flush()

def main(outpickle=OUTFILE, indir=IN_DIR):
	

	logging.debug('entered main)')
	all_files = [f for f in os.listdir(indir) if 'meta' not in f]
	l = []
	for i, filename in enumerate(all_files):
		update_progress((i+1.0)/len(all_files) * 100, i, len(all_files))
		for article_tup in get_articles(os.path.join(indir, filename)):
			l += [article_tup]
	with open(OUTFILE,'w') as out_f:
		json.dump(l, out_f)
		
	print("\n")
	logging.info('Done. Written out to %s' % OUTFILE)
	
if __name__=="__main__":
	import doctest
	doctest.testmod()
	logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
	main()