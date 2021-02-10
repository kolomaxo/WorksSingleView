import unicodedata


class Canonizer:

    def normalize_all(self, data_records_collection):
        for record in data_records_collection:
            self.normalize_one(record)
        return

    def normalize_one(self, data_record):
        data_record['normalized_title'] = self.string_remove_accents(data_record['title'].lower())
        data_record['contributors'] = data_record['contributors'].lower().split("|")
        data_record['normalized_contributors'] = [self.string_remove_accents(contributor)
                                                  for contributor in data_record['contributors']]
        return

    def string_remove_accents(self, unicode_string):
        string_nfkd_form = unicodedata.normalize('NFKD', unicode_string)
        return u"".join([c for c in string_nfkd_form if not unicodedata.combining(c)])
