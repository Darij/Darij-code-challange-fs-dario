from flask import Flask, request, jsonify
from backend import Suggester
app = Flask(__name__)


@app.route('/')
def root():
    return "This the root URL, you shouldn't be here, there's nothing here..."


@app.route('/suggestions', methods=['GET'])
def suggestions():
    q = request.args.get('q', None)
    min_rate = request.args.get('rate_minimum', None)
    skill = request.args.get('verified_skills', None)
    suggester = Suggester(q, min_rate, skill)
    suggester.search()
    result = jsonify(suggester.matches)
    return result
