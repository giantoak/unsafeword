from elasticsearch import Elasticsearch
from flask import Flask
from flask import jsonify
import pickle
app = Flask(__name__)

bad_dict = pickle.load(open('all_urls.pkl', 'rb'))
# this is a URI for ISI (I *believe*, nothing else.

@app.route('/isi/<path:isi_uri>')
def check_isi_ad():

    es = Elasticsearch(['https://darpamemex:darpamemex@esc.memexproxy.com/dig-latest/WebPage/_search'],
                       verify_certs=False)

    res = es.search(q='id:"{}"'.format(isi_uri))

    text = ''
    for key in ['hasTitlePart', 'hasBodyPart']:
        try:
            text += res['hits']['hits'][0]['_source'][key].lower().strip()
            text += ' '
        except AttributeError:
            # skip if no title or body
            pass

    # Tokenize the title and text, keeping tokens with at least one . in them
    toks = set(x for x in text.strip().split() if x.find('.') > -1)

    match_dict = {tok: bad_dict[tok] for tok in toks if tok in bad_dict}
    return jsonify(match_dict)

if __name__ == '__main__':
    app.run()
