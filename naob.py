#!/usr/bin/env python3

import requests
import logging
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json',
    'Origin': 'https://naob.no',
    'Connection': 'keep-alive',
    'Referer': 'https://naob.no/ordbok/test',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers',
}

#data = '{"word":"test"}'

#response = requests.post('https://naob.no/search-article', headers=headers, data=data)

class NaobDoc:
    def __init__(self, json):
        self.raw = json
        self.artid = json['artid']
        self.boeyningsform = json['boeyningsform']
        self.elementid = json['elementid']
        self.freetext = json['freetext']
        self.id = json['id']
        self.oppslagsord = json['oppslagsord']
        self.oppslagsordsize = json['oppslagsordsize']
        self.shortxmlcontent = json['shortxmlcontent']
        self.version = json['_version_']
        self.wordcombined = json['wordcombined']
        self.xmlcontent = json['xmlcontent']
    def __str__(self):
        return '\n'.join(self.freetext)

    __repr__ = __str__



def search_article(word):
    data = f'{{"word": "{word}"}}'
    response = requests.post('https://naob.no/search-article', headers=headers, data=data)
    if not response.ok:
        logging.error("Something wen't wrong")
    response = response.json()['data']['response']
    numFound = response['numFound']
    docs = response['docs']
    if numFound != len(docs):
        logging.warning(f'Response inconsistency {docs} docs / {numFound} advertized.')
    results = [NaobDoc(doc) for doc in docs]
    return results

docs = search_article("ipa")
print(docs[0])
