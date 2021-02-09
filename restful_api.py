import argparse
import flask
import flask_restful
import pymongo
import json
from bson import json_util




class WorksSingleViewAPI(flask_restful.Resource):
    def __init__(self):
        dbClient = pymongo.MongoClient(configuration['connection_string'])
        self.worksSingleViewDB = dbClient[configuration['mongo_database']]

    def get(self, work_iswc):
        work_document = self.worksSingleViewDB[configuration['collection']] \
            .find_one({"iswc": work_iswc},
                      {"_id": 0, "iswc": 1, "title": 1, "contributors": 1}
                      )
        print(type(work_document))
        return json.dumps(work_document, sort_keys=True, default=json_util.default)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="configuration_json",
                        type=str, help="path to json configuration file"
                        )
    args = parser.parse_args()
    with open(args.configuration_json, 'r') as configuration_json_file:
        configuration = json.load(configuration_json_file)
    app = flask.Flask(__name__)
    api = flask_restful.Api(app)
    api.add_resource(WorksSingleViewAPI, '/api/iswc/<string:work_iswc>')
    app.run()
