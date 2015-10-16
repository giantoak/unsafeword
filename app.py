from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from flask import Flask
from flask import jsonify
import pickle
import re
app = Flask(__name__)

bad_dict = pickle.load(open('all_urls.pkl', 'rb'))
isi_es = Elasticsearch(['https://darpamemex:darpamemex@esc.memexproxy.com/dig-latest/WebPage/'], verify_certs=False)
cdr_es = Elasticsearch(['https://memex:3vYAZ8bSztbxmznvhD4C@els.istresearch.com:19200/memex-domains/'],
                       verify_certs=False)

sub_expr = r'(www\.)|(https?://)'


def get_cdr_exact_url_filter_dsl(url):
    """
    Take a url, and return a dict for use with Query DSL that will match it exactly.
    This function primarily exists as a reference:
    The lucene query "q=url:<url>" will get the job done as well.
    :param str url: the url to match
    :return dict: A dictionary compatible with Elasticsearch's Query DSL
    """
    return {"query": {"filtered": {"filter": {"term": {"url.exact": str(url)}}}}}

def clean_entry(raw_text):
    """
    Take a url, return root forms of it.
    :param raw_text: Raw urls from spam lists
    :return: lists of cleaned urls generated from the raw
    """
    texts = list()
    texts.append(re.sub(sub_expr, '', raw_text).strip())
    for sep in ['?', ';']:
        if raw_text.find(sep) > -1:
            texts.append(raw_text.split(sep)[0].strip())
    return texts


def get_match_dict(raw_text):
    """
    Takes a raw text string and finds any URLS on the bad list. Returns a dict of them
    :param raw_text: ad text
    :return:
    """
    # Tokenize the title and text, keeping tokens with at least one . in them
    toks = set(x for x in raw_text.strip().split() if x.find('.') > -1)
    match_dict = dict()
    for tok in toks:
        for entry in clean_entry(tok):
            if entry in bad_dict:
                match_dict[entry] = bad_dict[entry]
    match_dict['spam_flag'] = len(match_dict) > 0
    return match_dict


def get_match_dict_from_es_query(es, query_str, text_fields):
    """
    Generic wrapper for getting matches on text stored in an Elasticsearch DB
    :param es: the elasticsearch connection to use
    :param query_str: the query string for the entry
    :param text_fields: The fields of the entry that contain text
    :return: A match dict for the specified entry
    """
    if not es.search_exists(q=query_str):
        return {'spam_flag': False}

    res = es.search(q=query_str, fields=text_fields)

    text = u''
    for key in text_fields:
        try:
            text += res['hits']['hits'][0]['fields'][key][0].lower().strip()
            text += ' '
        except (IndexError, AttributeError):
            # skip if no title or body
            pass

    text = text.strip()

    bs = BeautifulSoup(text, 'lxml')
    if bs.get_text() != text:
        text = (bs.get_text()+' '+' '.join(x['href'] for x in bs.find_all('a'))).strip()

    return get_match_dict(text)


@app.route("/")
def confirm_on():
    """ Debug test """
    return "The server's up."


@app.route('/raw')
def explain_raw():
    return "This app takes a string of ad text that needs to be evaluated:" \
           "<br>raw/<em>&lt;ad text&gt;</em>"


@app.route('/raw/<path:raw_text>')
def check_raw_ad(raw_text):
    """
    Check raw ad text for spam terms
    :param raw_text:
    :return:
    """
    return jsonify({'identifier': {'raw': raw_text},
                    'matches': get_match_dict(raw_text)})


@app.route('/isi')
def explain_isi():
    return "This app takes a uri field for ISI's Elasticsearch endpoint:" \
           "<br>isi/<em>&lt;uri&rt;</em>"


@app.route('/isi/<path:isi_uri>')
def check_isi_ad(isi_uri):
    """
    Take an ISI URI code, look up the corresponding ad text, and return a dict of spam URLs.
    :param isi_uri: The URI in the ISI Elasticsearch database
    :return unicode: json dictionary containing the URI, a spam_flag bool, and any of the spam urls
    """
    return jsonify({'identifier': {'uri': isi_uri},
                    'matches': get_match_dict_from_es_query(isi_es,
                                                            'uri:"{}"'.format(isi_uri),
                                                            ['hasTitlePart.text', 'hasBodyPart.text'])})

@app.route('/cdr')
def explain_cdr():
    return "This app takes a year, month, domain, and url field for the CDR's Elasticsearch endpoint:" \
           "<br>cdr:/<em>&lt;url&rt;</em>"


@app.route('/cdr/<path:cdr_url>')
def check_cdr_ad(cdr_url):
    """
    Take a CDR URL, look up the corresponding ad text, and return a dict of spam URLs.
    :param cdr_url: The URL in the CDR
    :return unicode: json dictionary containing the URI, a spam_flag bool, and any of the spam urls
    """
    return jsonify({'identifier': {'url': cdr_url},
                    'matches': get_match_dict_from_es_query(cdr_es,
                                                            'url:"{}"'.format(cdr_url),
                                                            ['raw_content', 'crawl_data.title', 'crawl_data.website'])})


if __name__ == '__main__':
    app.run()
