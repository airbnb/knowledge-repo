from builtins import object
import re


class SubstitutionMapper(object):

    def __init__(self, patterns={}, mappers=[]):
        self.mappers = mappers
        self.patterns = {name: re.compile(pattern)
                         for name, pattern in patterns.items()}

    def apply(self, text):
        matches = self.find_matches(text)
        output = []
        last_offset = 0

        for dmatch in matches:
            name, offset, match = dmatch['name'], dmatch[
                'offset'], dmatch['match']

            output.append(text[last_offset:offset])
            last_offset = offset + len(match.group(0))
            for mapper in self.mappers:
                replacement = mapper(name, match)
                if replacement is not None:
                    break
            if replacement is None:
                output.append(match.group(0))
            else:
                output.append(replacement)
        output.append(text[last_offset:])
        return ''.join(output)

    def find_matches(self, text, reverse=False):
        matches = []
        for name in self.patterns:
            matches.extend(self.find_matches_for_pattern(name, text))
        return sorted(matches, key=lambda x: x['offset'], reverse=reverse)

    def find_matches_for_pattern(self, name, text):
        return [{'name': name,
                 'offset': m.start(),
                 'match': m} for m in self.patterns[name].finditer(text)]
