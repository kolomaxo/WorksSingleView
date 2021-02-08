class Matcher:
    def __init__(self, distance_confidence, has_unique_key=False):
        self.clusters = {}
        self.unmatched_objects = []
        self.has_unique_key = has_unique_key
        self.distance_confidence = distance_confidence
        return

    def __canonize_clusters(self):
        for cluster in self.clusters.values():
            cluster.canonize()
        return

    def __distance_match_clustering(self, objects):
        for my_object in objects:
            best_match_key = None
            best_matching_score = self.distance_confidence
            for cluster in self.clusters.values():
                matching_score = cluster.calculate_distance(my_object)
                if matching_score > best_matching_score:
                    best_match_key = cluster.get_unique_key()
                    best_matching_score = matching_score
                if best_matching_score >= 1.0:
                    break
            if best_match_key is not None:
                self.clusters[best_match_key].merge(my_object)
                # self.cluster_class.merge(self.clusters[best_match_key], my_object)

    def __exact_match_clustering(self, objects):
        for my_object in objects:
            my_object_key = my_object.get_unique_key()
            if my_object_key in self.clusters.keys():
                self.clusters[my_object_key].merge(my_object)
                # self.cluster_class.merge(self.clusters[my_object_key], my_object)
            elif my_object_key is not None:
                self.clusters[my_object_key] = my_object
            else:
                self.unmatched_objects.append(my_object)

    def fit(self, records):
        print(type(records[0]))
        if self.has_unique_key:
            self.__exact_match_clustering(records)
        self.__canonize_clusters()

        self.__distance_match_clustering(self.unmatched_objects)
        self.__canonize_clusters()

        return self.clusters.values()

    def reset_all(self):
        self.reset_unmatched()
        self.clusters = []
        return

    def reset_unmatched(self):
        self.unmatched_objects = []
        return
