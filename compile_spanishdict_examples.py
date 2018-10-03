import re
import sys

import os
import requests
import random
from bs4 import BeautifulSoup

option_print_csv = False
if '--csv' in sys.argv:
	option_print_csv = True
	sys.argv.remove('--csv')

userAgent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36'}

def download_word(file_name, word):
	file_name = re.sub(r'[<>/]', '', file_name)
	file_path = 'aggr_html/' + file_name + '.html'
	if not os.path.exists(file_path):
		url = 'http://spanishdict.com/translate/%s' % word
		r = requests.get(url, headers = userAgent)
		open(file_path, 'w+').write(r.text)
	return open(file_path).read()

if not os.path.isdir('aggr_html'):
	os.makedirs('aggr_html')

# GET WORD LIST
verbs = open(sys.argv[1]).read()
verb_list = re.findall('([^\n—]+) — ([^\n~]+)(?: ~~~ )?([^\n]+)?', verbs)
random.Random(234234).shuffle(verb_list)

if not option_print_csv:
	print('<html><head><meta charset="utf-8"><style>body {font-family: "HoeflerText-Regular"}</style></head><body>')

# GO THROUGH WORD LIST
for en_orig,es_orig,ex_orig in verb_list:
	# CLEAN UP AND PROCESS WORDS
	en = re.sub(r' \(.+?\)', '', en_orig)
	en = re.sub(r'^to ', '', en)
	en = re.sub(r'\.+', '', en)
	en = en.strip()

	es = re.sub(r' \(.+?\)', '', es_orig)
	es = re.sub(r'\.+', '', es)
	es_list = re.split(r'[,;] ', es)
	es = es.strip()

	example_list = re.split(' ?~~~ ', ex_orig)
	
	# SPLIT PHRASES WITH SLASHES INTO TWO SEPARATE PHRASES.
	i = 0
	while i < len(es_list):
		es_ = es_list[i]
		alts = re.findall('([^\s]+)/([^\s]+)', es_)

		if alts and len(alts[0]) == 2:
			es_list[i] = es_.replace('/'.join(alts[0]), alts[0][0])
			es_list.insert(i+1, es_.replace('/'.join(alts[0]), alts[0][1]))
		i += 1

	# PRINT WORD HEADER
	if option_print_csv:
		print('"<span style=\'font-family:HoeflerText-Regular;font-size:20pt\'>{}</span>","<span style=\'font-family:HoeflerText-Regular;font-size:20pt\'>{}</span><br /><span style=\'font-family:HoeflerText-Regular;font-size:16pt\'>'.format(en, es), end='')
	else:
		print('<span style="color:#377DFF">{} — {}</span>'.format(en_orig, es_orig), end='')
	
	# PRINT EXISTING EXAMPLE (IF ANY)
	for ex in example_list:
		if ex != '':
			print('<br /><i>{}</i>'.format(ex), end='')

	# DOWNLOAD/OPEN AND PARSE HTML FILE.
	html = download_word(en_orig, en)
	parsed = BeautifulSoup(html, features="html.parser")
	in2_list = parsed.find_all('div', attrs={'class':'dictionary-neodict-indent-2'})

	# PARSE EXAMPLES
	N_examples = 0
	for a in in2_list:
		for b in a.contents:
			if b['class'][0] == 'dictionary-neodict-translation':
				c = b.find_all('a', attrs={'class':'dictionary-neodict-translation-translation'})
				es_word = c[0].text
				es_word = re.sub(r'( \(m\)|\(f\))', '', es_word)
				if es_word in es_list:
					do_print = True
				else:
					do_print = False
			elif b['class'][0] == 'dictionary-neodict-indent-3':
				if do_print:
					c = b.find_all('div', attrs={'class':'dictionary-neodict-example'})
					for d in c:
						if option_print_csv:
							es_sen = d.find_all('em')[0].text.replace('"', "'")
							print('<br /><i>{}</i>'.format(es_sen), end='')
						else:
							es_sen = d.find_all('em')[0].text
							print('<br /><i>{}</i>'.format(es_sen), end='')
						N_examples += 1

	if option_print_csv:
		print('</span>"\x0D\x0A', end='')
	else:
		print('<br /><br />')

if not option_print_csv:
	print('</html></body>')
