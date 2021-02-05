import flask
import flask_restful
import pymongo
import json
from bson import json_util

class HelloWorld(flask_restful.Resource):
    def __init__(self):
        dbClient = pymongo.MongoClient("mongodb://127.0.0.1:27017/?compressors=zlib")
        self.worksSingleViewDB = dbClient['WorksSingleViewDB']

    def get(self, work_iswc):
        work_document = self.worksSingleViewDB['WorksSingleViewCollection'].find({"iswc": work_iswc})[0]
        return json.dumps(work_document, sort_keys=True, default=json_util.default)


if __name__ == '__main__':
    app = flask.Flask(__name__)
    api = flask_restful.Api(app)
    api.add_resource(HelloWorld, '/api/iswc/<string:work_iswc>')

    app.run(debug=True)


