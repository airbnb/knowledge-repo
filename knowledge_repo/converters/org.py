import re

from ..converter import KnowledgePostConverter


def dict_to_yaml(x):
    yaml = ''
    for key, value in x.items():
        if type(value) == list:
            lines = "{key}:\n".format(key=key)
            for v in value:
                lines += "- {v}\n".format(v=v)
        else:
            lines = "{key}: {value}\n".format(key=key, value=value)

        yaml += lines

    return yaml


class OrgConverter(KnowledgePostConverter):
    '''
    Converts .org documents to the markdown syntax needed for a knowledge repo.

    Uses the .org metadata standard syntax to populate the metadata YAML required by the knowledge repo.
    (e.g. #+TITLE: the title becomes - title: the title)

    Metadata field equivalency:
    TITLE: title
    AUTHOR: authors
    DATE: created_at
    KR_UPDATED_AT: updated_at
    KR_TLDR: tldr
    KR_TAGS: tags

    Note that in orgmode, the convention for designating many authors is to separate them using commas like so:
    #+AUTHOR: author 1, author 2
    This convention was kept for every list element, so that
    #+KR_TAGS: tag1, tag2
    is the correct way to assign many tags to a post/document
    '''
    _registry_keys = ["org"]

    # This dict will help in converting org metadata (#+TITLE: {}) to yaml metadata (title: {})
    metadata_fields = {
        "title": {
            "type": "string",
            "converts_to": "title"
        },
        "author": {
            "type": "list",
            "converts_to": "authors"
        },
        "date": {
            "type": "string",
            "converts_to": "created_at"
        },
        "kr_updated_at": {
            "type": "string",
            "converts_to": "updated_at"
        },
        "kr_tldr": {
            "type": "string",
            "converts_to": "tldr"
        },
        "kr_tags": {
            "type": "list",
            "converts_to": "tags"
        }
    }

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of core knowledge-repo dependencies
        return []

    def from_file(self, filename, **opts):
        with open(filename, "r") as f:
            lines = f.readlines()

        self.kp.add_srcfile(filename)
        self.from_lines(lines, **opts)

    def from_string(self, string, **opts):
        lines = string.split("\n")

        self.from_lines(lines, **opts)

    def from_lines(self, lines, **opts):
        # These dict will let use the correct function for each line
        line_converters = {
            "src": self.convert_code,
            "text": self.convert_text,
            "example": self.convert_example
        }

        new_lines = []
        metadata = dict()
        in_chunk = False
        line_type = "text"
        for line in lines:
            new_line = new_meta = None

            # Resets the line_type if we're outside of a chunk
            if not in_chunk:
                line_type = "text"

            # Is this the beggining or end of a chunk?
            if line.lower().strip().startswith("#+begin_"):
                in_chunk = True
                line_type = re.search("#\+begin_(\w+)", line.lower()).group(1)
            elif line.lower().strip().startswith("#+end_"):
                in_chunk = False
            elif line.strip().startswith("#+") or line.strip().startswith("# -*-"):
                line_type = "meta"

            # Meta (org settings) never add a line to markdown
            if line_type == "meta":
                new_meta = self.extract_meta(line)
            elif line_type in line_converters:
                new_line = line_converters[line_type](line)

            if new_meta is not None:
                metadata.update(new_meta)

            if new_line is not None:
                new_lines.append(new_line)

        return self.write_kp(new_lines, metadata)

    def convert_text(self, line):
        '''
        Translates a single line of 'regular' text from orgmode syntax to markdown syntax
        '''

        new_line = line

        # Headers (Org: *Header)
        header_match = re.match("^(\*+)", new_line)
        if header_match:
            n_asts = len(header_match.group(1))
            new_line = re.sub("^(\*+)", "#" * n_asts, new_line)

        # Find and replace
        replacer_regex = [
            # TODO: inline source
            # TODO: strikethrough
            # Bold (*bold*)
            {
                "regex": re.compile(r"\B\*(?P<bolded>[^\*]+)\*\B", re.U),
                "replace_fmt": "**{bolded}**"
            },
            # Italics (/italics/)
            {
                "regex": re.compile(r"\B/(?P<italicized>[^/]+)/\B", re.U),
                "replace_fmt": "_{italicized}_"
            },
            # Hyperlinks ([[link][desc]])
            {
                "regex": re.compile("\[\[(?P<link>[^\[\]]+)\]\[(?P<desc>[^\[\]]+)\]\]"),
                "replace_fmt": "[{desc}]({link})"
            },
            # Images ([[imgpath]])
            {
                "regex": re.compile("\[\[(?P<imgpath>[^\[\]]+)\]\]"),
                "replace_fmt": "![]({imgpath})"
            }
        ]

        for args in replacer_regex:
            new_line = self.find_and_replace(new_line, **args)

        return new_line.strip()

    def find_and_replace(self, string, regex, replace_fmt):
        '''
        Finds every match of a regular expression with named groups and replaces it according to a specified
        format (format must also have names)

        :param string: original string
        :param regex: regex to find and replace
        :param replace_fmt: replace format, must have names
        '''
        new_string = string
        for match in re.finditer(regex, string):
            groups = match.groupdict()
            found = string[match.start():match.end()]

            new_string = new_string.replace(found, replace_fmt.format(**groups))

        return new_string

    def extract_meta(self, line):
        meta = None
        line = line.strip()
        for field in self.metadata_fields:
            if line.lower().startswith("#+{}:".format(field)):
                field_type = self.metadata_fields[field]["type"]
                field_name = self.metadata_fields[field]["converts_to"]

                if field_type == "list":
                    value = line.split(":")[1].split(",")
                else:
                    value = line.split(":")[1]

                meta = {field_name: value}
                break

        return meta

    def convert_code(self, line):
        '''
        Translates a single line of a code block in orgmode syntax to markdown syntax.
        '''
        if "#+begin_src" in line.lower():
            new_line = "```"

            # language is always immediately after BEGIN_SRC
            opts = line.strip().split(" ")
            if len(opts) > 1:
                new_line += opts[1]

        elif "#+end_src" in line.lower():
            new_line = "```"
        else:
            new_line = line

        return new_line.strip()

    def convert_example(self, line):
        '''
        Translates a single line of an 'example' block in orgmode syntax to markdown syntax
        '''
        if "#+begin_example" in line.lower() or "#+end_example" in line.lower():
            return None

        return "    " + line.strip()

    def write_kp(self, new_lines, metadata):
        # Metadata header
        metadata_str = "---\n{}\n---".format(dict_to_yaml(metadata))

        body = metadata_str + "\n".join(new_lines)

        self.kp.write(body)
