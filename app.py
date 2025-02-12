#application web crawler
from flask import Flask, request, jsonify
from flask_cors import CORS
from crawler import Crawler

app = Flask(__name__)
CORS(app)

@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.get_json()
    url = data['url']
    crawler = Crawler(url)
    return jsonify(crawler.crawl())

if __name__ == '__main__':
    app.run(debug=True)

    

