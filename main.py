import csv
from csv import Dialect

import pymongo
from components.MediaCluster import MediaCluster
from components.SimpleMatcher import Matcher
from pprint import pprint
import re

INPUT_FILE_LOCATION = "works_metadata.csv"
INPUT_FILE_ENCODING = "utf8"
FUZZY_MATCH_CONFIDENCE = 0.7

if __name__ == '__main__':

    raw_clusters = []

    with open(INPUT_FILE_LOCATION, encoding=INPUT_FILE_ENCODING) as csv_input_file:
        csv_reader = csv.DictReader(csv_input_file)
        iswc_re = re.compile("T\d{10}")

        for record in csv_reader:
            record['contributors'] = record['contributors'].split("|")
            if not iswc_re.match(record['iswc']):
                record['iswc'] = None

            new_media_cluster = MediaCluster(record)
            raw_clusters.append(new_media_cluster)

    clustering_method = Matcher(distance_confidence=FUZZY_MATCH_CONFIDENCE, has_unique_key=True)
    merged_clusters = clustering_method.fit(raw_clusters)
    del raw_clusters

    merged_clusters_list = [cluster.to_dict() for cluster in merged_clusters]
    del merged_clusters
    for cl in merged_clusters_list:
        pprint(cl)

'''
    dbClient = pymongo.MongoClient("mongodb://127.0.0.1:27017/?compressors=zlib")
    worksSingleViewDB = dbClient['WorksSingleViewDB']
    worksSingleViewDB['WorksSingleViewCollection'].insert_many(inputFileDataDict, ordered=False)
'''