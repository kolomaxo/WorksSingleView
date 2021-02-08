import math
import textdistance
from components.Canonizer import Canonizer


class MediaCluster:

    def __init__(self, media_record=None):
        self.canonizer = Canonizer()

        self.title_candidates = []
        self.contributors_all = []
        self.iswc = None

        self.title = None
        self.canonized_title = None
        self.contributors = []

        if media_record is not None:
            self.iswc = media_record["iswc"]
            self.add_title(media_record['title'])
            self.add_contributors(media_record["contributors"])

        return

    def __normalized_levenshtein(self, string, another_string):
        norm = len(string) + len(another_string)
        normalized_levenshtein_distance = 0.0
        if norm != 0:
            normalized_levenshtein_distance = textdistance.levenshtein.distance(string, another_string) / norm
        return normalized_levenshtein_distance

    def add_contributors(self, contributors):
        if isinstance(contributors, str):
            self.contributors_all.append(contributors)
        else:
            self.contributors_all.extend(contributors)
        return

    def add_title(self, titles):
        if isinstance(titles, str):
            self.title_candidates.append(titles)
        else:
            self.title_candidates.extend(titles)
        return

    def calculate_distance(self, another_cluster):
        if self.canonized_title is None:
            self.canonize()
        if another_cluster.canonized_title is None:
            another_cluster.canonize()
        title_match_score = 1 - self.__normalized_levenshtein(self.canonized_title,
                                                              another_cluster.canonized_title)
        contributors_inclusion_score = 0.0
        for contributor in another_cluster.contributors_all:
            seted_contributor = set(contributor.lower().split(' '))
            for seted_cluster_contributor, _tmp in self.contributors:
                if seted_contributor.issubset(seted_cluster_contributor):
                    contributors_inclusion_score += 1.0
                else:
                    contributors_inclusion_score -= 0.5
        contributors_inclusion_score /= len(another_cluster.contributors)
        distance = 0.7 * title_match_score + 0.3 * contributors_inclusion_score
        return distance

    def canonize(self):
        self.set_titles()
        self.set_contributors()
        return

    def get_unique_key(self):
        return self.iswc

    def merge(self, another_cluster):
        self.add_title(another_cluster.title_candidates)
        self.add_contributors(another_cluster.contributors_all)
        return

    def set_titles(self):
        best_title = None
        best_canonized_title = None
        canonization_distance = math.inf
        for title in self.title_candidates:
            canonized_title = self.canonizer.string_remove_accents(title.lower())
            distance = self.__normalized_levenshtein(title, canonized_title)
            if distance < canonization_distance:
                best_canonized_title = canonized_title
                best_title = title
                canonization_distance = distance
        self.canonized_title = best_canonized_title
        self.title = best_title
        return

    def set_contributors(self):
        self.contributors_all.sort(key=len, reverse=True)
        for contributor in self.contributors_all:
            contributor = self.canonizer.string_remove_accents(contributor)
            seted_contributor = set(contributor.lower().split(' '))
            for (seted_existing_contributor, existing_contributor) in self.contributors:
                if seted_contributor.issubset(seted_existing_contributor):
                    break
            else:
                self.contributors.append((seted_contributor, contributor))
        return

    def to_dict(self):
        _dict = {"iswc": self.iswc,
                 "title": self.title,
                 "contributors": []
                }
        for _tmp, contributor in self.contributors:
            _dict["contributors"].append(contributor)
        return _dict


