from flask import Flask
from flask import jsonify
import pickle
app = Flask(__name__)


bad_dict = pickle.load(open('all_urls.pkl', 'rb'))


@app.route('/')
def check_ad_text():
    ad_text = 'just some test text. XXXX!'

    # Keep tokens with at least one . in them
    toks = set(x for x in ad_text.strip().split() if x.find('.') > -1)

    match_dict = {tok: bad_dict[tok] for tok in toks if tok in bad_dict}
    return jsonify(match_dict)

if __name__ == '__main__':
    app.run()
