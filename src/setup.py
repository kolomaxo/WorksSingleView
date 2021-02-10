import pymongo
import time
import argparse
import json


MONGO_USER = "mongo_user"
MONGO_PWD = "mongo_pwd"
MONGO_ADDRESS = "mongo_address"
MONGO_DATABASE_NAME = 'mongo_db'
MONGO_COLLECTION_PREFIX = 'mongo_collection'
CONFIGURATION_FILE_PATH = "configuration/internal_config.json"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="configuration_json", type=str, help="path to json configuration file")
    args = parser.parse_args()
    with open(args.configuration_json, 'r') as configuration_json_file:
        config = json.load(configuration_json_file)

    mongo_connection_string = "mongodb://" + config[MONGO_USER] + ":" + config[MONGO_PWD] + "@" \
                              + config[MONGO_ADDRESS] + "/?compressors=zlib"
    dbClient = pymongo.MongoClient(mongo_connection_string)
    database = dbClient[config[MONGO_DATABASE_NAME]]
    collection_name = config[MONGO_COLLECTION_PREFIX] + str(round(time.time() * 1000))
    database.create_collection(collection_name)
    with open(CONFIGURATION_FILE_PATH, 'w') as configuration_file_json:
        json.dump({'collection': collection_name,
                   'connection_string': mongo_connection_string,
                   'mongo_database': config[MONGO_DATABASE_NAME]}, configuration_file_json)
    dbClient.close()
