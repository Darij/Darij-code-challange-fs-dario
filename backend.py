import json


class Suggester:
    """Object to query and return results as suggestions
    """

    def __init__(self):
        with open('generated.json', 'r') as file:
            self.data = json.load(file)
            self.q_matches = []
            self.rate_matches = []
            self.skill_matches = []
            self.matches = []

    def _values_match(self, query, data):
        """Compares type of data for
            filter and data in json
            before comparing if they match

        Arguments:
            query {[string]} -- query filter
            data {[json]}

        Returns:
            [boolean] -- [if values match or not]
        """
        if type(query) == type(data):
            if query == data:
                return True
            elif query in data:
                return True
            else:
                return False
        else:
            return False

    def _sortResults(self):
        for entry in self.q_matches:
            count = 1
            if entry in self.skill_matches:
                self.skill_matches.remove(entry)
                count = count + 1
            if entry in self.rate_matches:
                self.rate_matches.remove(entry)
                count = count + 1
            entry['score'] = count / 3

        for entry in self.rate_matches:
            count = 1
            if entry in self.skill_matches:
                self.skill_matches.remove(entry)
                count = count + 1
            entry['score'] = count / 3

        for entry in self.skill_matches:
            count = 1
            entry['score'] = count / 3

        self.matches = self.q_matches + self.rate_matches + self.skill_matches

    def search(self, query, rate, skill):
        """Query data, sorts
           records if matched with filters
        """
        if query is not None:
            for entry in self.data:
                for field in entry:
                    if self._values_match(query, entry[field]):
                        self.q_matches.append(entry)

        if rate is not None:
            for entry in self.data:
                if rate in entry['min_rate']:
                    self.rate_matches.append(entry)

        if skill is not None:
            for entry in self.data:
                if skill in entry['verified_skills']:
                    self.skill_matches.append(entry)

        self._sortResults()
