import pymongo
import time
import json

MONGO_CONNECTION_STRING = "mongodb://readWriter:qwertz@127.0.0.1:27017/?compressors=zlib"
MONGO_DATABASE_NAME = 'WorksSingleViewDB'
MONGO_COLLECTION_PREFIX = 'WorksSingleViewCollection_'
CONFIG_FILE_PATH = "config.cfg"

if __name__ == '__main__':
    dbClient = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    database = dbClient[MONGO_DATABASE_NAME]
    collection_name = MONGO_COLLECTION_PREFIX + str(round(time.time() * 1000))
    database.create_collection(collection_name)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump({'collection': collection_name}, config_file)

    dbClient.close()