import json


class Suggester:
    """Object to query and return results as suggestions
    """

    def __init__(self, qFilter, rFilter, sFilter):
        self.matches = []
        self.q_filter = qFilter
        self.rate_filter = rFilter
        self.skill_filter = sFilter
        self.num_filters = 0
        with open('generated.json', 'r') as file:
            self.data = json.load(file)

        if qFilter:
            self.num_filters += 1
        if rFilter:
            self.num_filters += 1
        if sFilter:
            self.num_filters += 1

    def _get_comparer(self, sfilter, list_field):
        """If field comparer is a list,
        extract element that resembles
        filter the most by comparing
        length differences.

        Arguments:
            sfilter {[string]} -- [filter from self to use]
            list_field {[list]} -- [field in matched query]

        Returns:
            Lenght of field to compare
        """
        field_comp = None
        curr_lenght = 20  # Initial dummy value

        for value in list_field:
            if sfilter in value:
                temp_lenght = len(value) - len(sfilter)
                if temp_lenght < curr_lenght:
                    curr_lenght = temp_lenght
                    field_comp = value

        return field_comp

    def _sum_confidence(self, len_filter, len_field):
        """ Calculate percentage of how much one word matches another
            and add it total confidence
            Divide by number of filter used

        Arguments:
            len_filter {[int]} -- length of filter
            len_field {[int]} -- length of field
        """
        confidence = len_filter / len_field
        confidence = confidence / self.num_filters
        return confidence

    def _compareStrings(self, ufilter, field):
        """Procedure to compare filter
        and string field

        Arguments:
            skill {[string]}
            ufield {[string]} -- Using filter
        """
        confidence = 0
        filter_length = 0
        field_length = len(field)

        if isinstance(field, list):
            field = self._get_comparer(ufilter, field)

            if field is not None:
                field_length = len(field)

        if field is not None and ufilter in field:
            filter_length = len(ufilter)

            confidence = self._sum_confidence(filter_length, field_length)

        return confidence

    def _calculate_Confidence(self, entry):
        """Calculate the % of match confidence
        by comparing the similarity between
        matched field and filters

        Arguments:
            entry {[json object]} -- [object with employee data]
        """
        for field in entry['matched_fields']:
            confidence = 0
            field_length = len(field)

            if self.rate_filter and self.rate_filter in field:
                filter_length = len(self.rate_filter)
                confidence += self._sum_confidence(filter_length, field_length)

            if self.skill_filter:
                confidence += self._compareStrings(self.skill_filter, field)

            if self.q_filter:
                confidence += self._compareStrings(self.q_filter, field)

            entry['score'] += confidence

    def _values_match(self, query, data):
        """Compares the type of data in
            filter and json field
            before comparing value

        Arguments:
            query {[string]} -- query filter
            data {[json]}

        Returns:
            [boolean] -- [if values match or not]
        """
        if isinstance(data, list) and query in data:
            return True
        elif type(query) == type(data) and query in data:
            return True
        else:
            return False

    def _sortResults(self):

        def by_score(e):
            return e['score']

        for entry in self.matches:
            self._calculate_Confidence(entry)

        self.matches.sort(key=by_score, reverse=True)

    def search(self):
        """Query data, sorts
           records if matched with filters
        """

        for entry in self.data:

            matched_fields = []
            entry['matched'] = False

            if self.rate_filter is not None:
                # fix $sign bug
                if self.rate_filter in entry['min_rate']:
                    matched_fields.append(entry['min_rate'])
                    entry['matched'] = True

            if self.skill_filter is not None:
                if self.skill_filter in entry['verified_skills']:
                    if entry['verified_skills'] not in matched_fields:
                        matched_fields.append(entry['verified_skills'])
                        entry['matched'] = True

            if self.q_filter is not None:
                for field in entry:
                    if self._values_match(self.q_filter, entry[field]):
                        if entry[field] not in matched_fields:
                            matched_fields.append(entry[field])
                            entry['matched'] = True

            if entry['matched']:
                entry['matched_fields'] = matched_fields
                self.matches.append(entry)

        self._sortResults()
