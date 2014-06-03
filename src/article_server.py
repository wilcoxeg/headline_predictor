#!/usr/bin/env python2.7

DATASET='small'
PATH_FULL_JSON = "../data/raw/%s.json" % DATASET
PATH_POS_JSON = "../data/pos/%s.json" % DATASET

from bottle import route, run, template
import json
data = []
data_pos = []


@route('/raw_article/<id_str>')
def single_raw(id_str):
	global data
	id = int(id_str)
	if id>=0 and id<len(data):
		return str(data[id])
	else:
		return {}

@route('/raw_range/<id_start_str>/<id_end_str>')
def range_raw(id_start_str, id_end_str):
	ids = int(id_start_str)
	ide = int(id_end_str)
	if ids >= 0 and ids < ide:
		if ide - ids > 500:
			return "LIMIT RANGE TO 500 articles"
		return str(data[ids:ide])
	else:
		return "BAD REQUEST"

@route('/pos_article/<id_str>')
def single_pos(id_str):
	global data
	id = int(id_str)
	if id>=0 and id<len(data_pos):
		return str(data_pos[id])
	else:
		return {}

@route('/pos_range/<id_start_str>/<id_end_str>')
def range_pos(id_start_str, id_end_str):
	ids = int(id_start_str)
	ide = int(id_end_str)
	if ids >= 0 and ids < ide:
		if ide - ids > 500:
			return "LIMIT RANGE TO 500 articles"
		return repr(data_pos[ids:ide])
	else:
		return "BAD REQUEST"

with open(PATH_FULL_JSON) as pfj:
	data = json.load(pfj)

with open(PATH_POS_JSON) as ppj:
	data_pos = json.load(ppj)

run(host='localhost', port=8898)
