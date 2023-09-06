import json


class HVDataModel:
    def __init__(self, identifiers, location, dates, types, significance, summary, additional, report):
        self.report = report
        self.identifiers = identifiers
        self.location = location
        self.dates = dates
        self.types = types
        self.significance = significance
        self.summary = summary
        self.additional = additional

    def toHTML(self):
        print(self.report)
        print(self.identifiers)
        print(self.dates)
        print(self.types)
        result = "<b>{0}</b>\n" \
                 "<p>ids:{1}</p>\n" \
                 "<p>dates:{2}</p>\n" \
                 "<p>types:{3}</p>".format(self.report,
                                           self.identifiers,
                                           self.dates,
                                           self.types)
        return result

    def toDBQuery(self):
        identifiers = json.dumps(self.identifiers)
        dates = json.dumps(self.dates)
        types = json.dumps(self.types)
        additional = json.dumps(self.additional)
        location = "ST_GeomFromText('POINT({0} {1})', 4326)".format(self.location.x, self.location.y)
        query = """INSERT INTO HVReport VALUES ('{0}', '{1}', '{2}', '{3}','{4}', '{5}', '{6}', {7})""".format(
            self.report.replace("'", ""),
            identifiers.replace("'", ""),
            dates.replace("'", ""),
            types.replace("'", ""),
            self.significance.replace("'", ""),
            self.summary.replace("'", ""),
            additional.replace("'", ""),
            location
        )
        return query
