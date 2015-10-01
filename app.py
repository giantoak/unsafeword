from elasticsearch import Elasticsearch
from flask import Flask
from flask import jsonify
import pickle
import re
app = Flask(__name__)

bad_dict = pickle.load(open('all_urls.pkl', 'rb'))
isi_es = Elasticsearch(['https://darpamemex:darpamemex@esc.memexproxy.com/dig-latest/WebPage/'], verify_certs=False)
sub_expr = r'(www\.)|(https?://)'


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


@app.route("/")
def confirm_on():
    return "The server's up."


@app.route('/raw')
def explain_raw():
    return "This app takes a string of ad text that needs to be evaluated: raw/[ad text]"

@app.route('/raw/<path:raw_text>')
def check_raw_ad(raw_text):
    return jsonify(get_match_dict(raw_text))


@app.route('/isi')
def explain_isi():
    return "This app takes a uri field for ISI's Elasticsearch endpoint: isi/[uri]"

@app.route('/isi/<path:isi_uri>')
def check_isi_ad(isi_uri):
    """
    Take an ISI URI code, look up the corresponding ad text, and return a dict of spam URLs.
    :param isi_uri: The URI in the ISI Elasticsearch database
    :return unicode: json dictionary containing the URI, a spam_flag bool, and any of the spam urls
    """
    text_fields = ['hasTitlePart.text', 'hasBodyPart.text']

    res = isi_es.search(q='uri:"{}"'.format(isi_uri), fields=text_fields)

    text = u''
    for key in text_fields:
        try:
            text += res['hits']['hits'][0]['fields'][key].lower().strip()
            text += ' '
        except (IndexError, AttributeError):
            # skip if no title or body
            pass

    match_dict = get_match_dict(text)
    match_dict['uri'] = isi_uri
    return jsonify(match_dict)

if __name__ == '__main__':
    app.run()
