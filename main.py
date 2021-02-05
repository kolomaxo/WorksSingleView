import pandas
import pymongo
import unicodedata
import textdistance
from pprint import pprint
import math
import re

class Normalizer:
    def string_remove_accents(self, unicode_string):
            string_nfkd_form = unicodedata.normalize('NFKD', unicode_string)
            return u"".join([c for c in string_nfkd_form if not unicodedata.combining(c)])

    def normalize_one(self, data_record):
        data_record['normalized_title'] = self.string_remove_accents(data_record['title'].lower())
        data_record['contributors'] = data_record['contributors'].lower().split("|")
        data_record['normalized_contributors'] = [self.string_remove_accents(contributor)
                                                  for contributor in data_record['contributors']]
        return

    def normalize_all(self, data_records_collection):
        for record in data_records_collection:
            self.normalize_one(record)
        return





class Matcher:
    class MediaCluster:
        def __init__(self, iswc):
            self.title_candidates = []
            self.contributors_all = []
            self.canonized_title = None
            self.contributors = []
            self.title = None
            self.iswc = iswc
            return

        def to_dict(self):
            _dict = {}
            _dict["iswc"] = self.iswc
            _dict["title"] = self.title
            _dict["contributors"] = []
            for tmp, contributor in self.contributors:
                _dict["contributors"].append(contributor)
            return _dict

        def add_title(self, title):
            self.title_candidates.append(title)
            return

        def add_contributors(self, contributors):
            self.contributors_all.extend(contributors)
            return

        def set_titles(self):
            best_title = None
            best_canonized_title = None
            canonization_distance = math.inf
            for title in self.title_candidates:
                title = title.lower()
                canonized_title = Normalizer().string_remove_accents(title)
                distance = Matcher().normalized_levenshtein(title, canonized_title)
                if distance < canonization_distance:
                    best_canonized_title = canonized_title
                    best_title = title
                    canonization_distance  = distance
            self.canonized_title = best_canonized_title
            self.title = best_title
            return


        def set_contributors(self):
            self.contributors_all.sort(key=len, reverse=True)
            for contributor in self.contributors_all:
                contributor = Normalizer().string_remove_accents(contributor)
                seted_contributor = set(contributor.lower().split(' '))
                for (seted_existing_contributor, existing_contributor) in self.contributors:
                    if seted_contributor.issubset(seted_existing_contributor):
                        break
                else:
                    self.contributors.append((seted_contributor, contributor))
            return


    def __init__(self):
        self.clusters = {}
        return

    def normalized_levenshtein(self, string, another_string):
        norm = len(string) + len(another_string)
        normalized_levenshtein_distance = 0.0
        if norm != 0:
            normalized_levenshtein_distance = textdistance.levenshtein.distance(string, another_string) / norm
        return normalized_levenshtein_distance

    def process(self, records):
        unmatched_records = []
        for record in records:
            iswc = record["iswc"]
            if iswc in self.clusters.keys():
                self.clusters[iswc].add_title(record['title'])
                self.clusters[iswc].add_contributors(record['contributors'])
            elif iswc is not None:
                new_cluster = Matcher.MediaCluster(iswc)
                self.clusters[iswc] = new_cluster
                self.clusters[iswc].add_title(record['title'])
                self.clusters[iswc].add_contributors(record['contributors'])
            else:
                unmatched_records.append(record)

        for cluster in self.clusters.values():
            cluster.set_titles()
            cluster.set_contributors()

        for record in unmatched_records:
            best_match = None
            best_matching_score = 0.7
            for cluster in self.clusters.values():
                matching_score = self.fuzzy_match(record, cluster)
                if matching_score > best_matching_score:
                    best_match = cluster.iswc
                    best_matching_score = matching_score
                if best_matching_score >= 1.0:
                    break

            if best_match is not None:
                self.clusters[iswc].add_title(record['title'])
                self.clusters[iswc].add_contributors(record['contributors'])

        for cluster in self.clusters.values():
            cluster.set_titles()
            cluster.set_contributors()

        return [cluster.to_dict() for cluster in self.clusters.values()]

    def fuzzy_match(self, record, cluster):
                record_canonized_title = Normalizer().string_remove_accents(record['title'])
                title_match_score = 1 - self.normalized_levenshtein(record_canonized_title.lower(),
                                                                cluster.canonized_title)
                contributors_inclusion_score = 0.0
                for contributor in record['contributors']:
                    contributor = Normalizer().string_remove_accents(contributor)
                    seted_contributor = set(contributor.lower().split(' '))
                    for seted_cluster_contributor, _tmp in cluster.contributors:
                        if seted_contributor.issubset(seted_cluster_contributor):
                            contributors_inclusion_score += 1.0
                        else:
                            contributors_inclusion_score -= 0.5
                contributors_inclusion_score /= len(record['contributors'])
                fuzzy_match_score = 0.7 * title_match_score + 0.3 * contributors_inclusion_score
                return fuzzy_match_score



if __name__ == '__main__':
    inputFileDataFrame = pandas.read_csv('works_metadata.csv', header=0, keep_default_na=False)
    #inputFileDataFrame = inputFileDataFrame.drop('id', axis=1)
    inputFileDataDict = inputFileDataFrame.to_dict('records')
    iswc_re = re.compile("T\d{10}")
    for record in inputFileDataDict:
        record['contributors'] = record['contributors'].split("|")
        if not iswc_re.match(record['iswc']):
            record['iswc'] = None

    data_Processor = Matcher()
    inputFileDataDict = data_Processor.process(inputFileDataDict)
    pprint(inputFileDataDict)
    #Normalizer().normalize_all(inputFileDataDict)
    dbClient = pymongo.MongoClient("mongodb://127.0.0.1:27017/?compressors=zlib")
    worksSingleViewDB = dbClient['WorksSingleViewDB']
    worksSingleViewDB['WorksSingleViewCollection'].insert_many(inputFileDataDict, ordered=False)
