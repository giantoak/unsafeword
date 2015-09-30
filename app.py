from elasticsearch import Elasticsearch
from flask import Flask
from flask import jsonify
import pickle
app = Flask(__name__)

bad_dict = pickle.load(open('all_urls_2.pkl', 'rb'))

isi_es = Elasticsearch(['https://darpamemex:darpamemex@esc.memexproxy.com/dig-latest/WebPage/'], verify_certs=False)


@app.route("/")
def confirm():
    return "The server's up."

@app.route('/isi')
def explain_isi():
    return "This app takes a uri field for ISI's Elasticsearch endpoint: isi/[uri]"

@app.route('/isi/<path:isi_uri>')
def check_isi_ad(isi_uri):

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

    # Tokenize the title and text, keeping tokens with at least one . in them
    toks = set(x for x in text.strip().split() if x.find('.') > -1)

    match_dict = {tok: bad_dict[tok] for tok in toks if tok in bad_dict}
    match_dict['uri'] = isi_uri
    return jsonify(match_dict)

if __name__ == '__main__':
    app.run()
