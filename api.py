from flask import Flask, request
from flask_restful import Resource, Api
import kryssord

PORT = 5000

app = Flask(__name__)
api = Api(app)

class LandingPage(Resource):
    def get(self):
        return '/search/<query>[/pattern]'

class Query(Resource):
    def get(self, a):
        s = kryssord.Search(a)
        return {
            'nresults': s.nResults,
            'results': s.results,
            'uri': s.uri
        }

class QueryPattern(Resource):
    def get(self, a, b):
        s = kryssord.Search(a, b)
        return {
            'nresults': s.nResults,
            'results': s.results,
            'uri': s.uri
        }

api.add_resource(LandingPage, '/')
api.add_resource(Query, '/search/<a>')
api.add_resource(QueryPattern, '/search/<a>/<b>')


if __name__ == '__main__':
     app.run(port=str(PORT))
