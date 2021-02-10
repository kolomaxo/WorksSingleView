import argparse
import csv
import json
import pymongo
import re

from components.MediaCluster import MediaCluster
from components.SimpleMatcher import Matcher


INPUT_FILE_ENCODING = "utf8"
FUZZY_MATCH_CONFIDENCE = 0.7

MONGO_CONNECTION_STRING = "connection_string"
MONGO_DATABASE = "mongo_database"
MONGO_COLLECTION = "collection"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="configuration_json",
                        type=str, help="path to json configuration file"
                        )
    parser.add_argument("--match_confidence", dest="match_confidence",
                        type=float, help="float between 0.0 and 1.0; "
                                         "minimal confidence to match two records while clustering"
                        )
    parser.add_argument("--data", dest="input_file",
                        type=str, help="path to csv file with input data")

    args = parser.parse_args()
    with open(args.configuration_json, 'r') as configuration_json_file:
        mongo_configuration = json.load(configuration_json_file)

    raw_clusters = []
    with open(args.input_file, encoding=INPUT_FILE_ENCODING) as csv_input_file:
        csv_reader = csv.DictReader(csv_input_file)
        iswc_re = re.compile("T\d{10}")

        for record in csv_reader:
            record['contributors'] = record['contributors'].split("|")
            if not iswc_re.match(record['iswc']):
                record['iswc'] = None

            new_media_cluster = MediaCluster(record)
            raw_clusters.append(new_media_cluster)

    clustering_method = Matcher(distance_confidence=args.match_confidence, has_unique_key=True)
    merged_clusters = clustering_method.fit(raw_clusters)
    del raw_clusters

    merged_clusters_list = [cluster.to_dict() for cluster in merged_clusters]
    del merged_clusters

    dbClient = pymongo.MongoClient(mongo_configuration[MONGO_CONNECTION_STRING])
    worksSingleViewDB = dbClient[mongo_configuration[MONGO_DATABASE]]
    worksSingleViewDB[mongo_configuration[MONGO_COLLECTION]].insert_many(merged_clusters_list, ordered=False)
    worksSingleViewDB[mongo_configuration[MONGO_COLLECTION]].create_index('iswc')
    dbClient.close()
