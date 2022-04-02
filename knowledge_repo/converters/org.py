from ..constants import ORG
from ..converter import KnowledgePostConverter
from knowledge_repo.utils.files import read_text_lines
import re


def dict_to_yaml(x):
    yaml = []
    for key, value in x.items():
        if type(value) == list:
            yaml += f'{key}:\n'
            for v in value:
                yaml += f'- {v}\n'
        else:
            yaml += f'{key}: {value}\n'
    return ''.join(yaml)


class OrgConverter(KnowledgePostConverter):
    '''
    Converts .org documents to the markdown syntax needed for a knowledge repo.

    Uses the .org metadata standard syntax to populate the metadata YAML
    required by the knowledge repo.
    (e.g. #+TITLE: the title becomes - title: the title)

    Metadata required fields equivalency:
    TITLE: title
    AUTHOR: authors
    DATE: created_at
    DESCRIPTION: tldr
    KEYWORDS: tags

    For optional fields, the syntax is as follows
    #+KNOWLEDGE_REPO: :updated_at <date> :thumbnail <number>

    The names are the same as the YAML header

    Note that in orgmode, the convention for designating many authors is to
     separate them using commas like so:
    #+AUTHOR: author 1, author 2
    This convention was kept for every list element, so that
    #+KR_TAGS: tag1, tag2
    is the correct way to assign many tags to a post/document
    '''
    _registry_keys = [ORG]

    # This dicts will help in converting org metadata (#+TITLE: {})
    # to yaml metadata (title: {})
    metadata_required_fields = {
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
        "description": {
            "type": "string",
            "converts_to": "tldr"
        },
        "keywords": {
            "type": "list",
            "converts_to": "tags"
        }
    }

    metadata_optional_fields = {
        "updated_at": {
            "type": "string"
        },
        "path": {
            "type": "string"
        },
        "thumbnail": {
            "type": "string"
        },
        "private": {
            "type": "string"
        },
        "allowed_groups": {
            "type": "list"
        }
    }

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of
        # core knowledge-repo dependencies
        return []

    def from_file(self, filename, **opts):
        lines = read_text_lines(filename)

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
            "example": self.convert_example,
            "results": self.convert_example
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
            clean_line = line.lower().strip()
            if clean_line.startswith("#+begin_"):
                in_chunk = True
                line_type = re.search(r"#\+begin_(\w+)", clean_line).group(1)
            elif clean_line.strip().startswith("#+end_"):
                in_chunk = False
            # Special case for chunk start and end for results block
            elif clean_line.startswith("#+results"):
                in_chunk = True
                line_type = "results"
            elif line_type == "results" and not clean_line.startswith(":"):
                in_chunk = False
            elif clean_line.startswith("#+") or clean_line.startswith("# -*-"):
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
        Translates a single line of 'regular' text from orgmode syntax
        to markdown syntax
        '''

        new_line = line

        # Headers (Org: *Header)
        header_match = re.match(r"^(\*+)", new_line)
        if header_match:
            n_asts = len(header_match.group(1))
            new_line = re.sub(r"^(\*+)", "#" * n_asts, new_line)

        # Find and replace
        replacer_regex = [
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
                "regex": re.compile(r"\[\[(?P<link>[^\[\]]+)\]\[(?P<desc>[^\[\]]+)\]\]"),
                "replace_fmt": "[{desc}]({link})"
            },
            # Images ([[imgpath]])
            {
                "regex": re.compile(r"\[\[(?P<imgpath>[^\[\]]+)\]\]"),
                "replace_fmt": "![]({imgpath})"
            },
            # Code/verbatim (~verbatim~  or =verbatim=)
            {
                "regex": re.compile(r"\B[~=](?P<verbatim>[^~=]+)[~=]\B", re.U),
                "replace_fmt": "`{verbatim}`"
            },
            # Strikethrough (+strikethrough+)
            {
                "regex": re.compile(r"\B\+(?P<strikethrough>[^\+]+)\+\B", re.U),
                "replace_fmt": "~~{strikethrough}~~"
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

            new_string = new_string.replace(
                found, replace_fmt.format(**groups))

        return new_string

    def extract_meta(self, line):
        line = line.strip()
        if line.startswith("#+KNOWLEDGE_REPO"):
            return self.extract_optional_meta(line)
        else:
            return self.extract_required_meta(line)

    def extract_optional_meta(self, line):
        meta = dict()
        line = line.replace("#+KNOWLEDGE_REPO:", "").strip()

        prop_definitions = line.split(":")
        if len(prop_definitions) > 1:  # Else line is empty
            for prop_def in prop_definitions[1:]:
                prop_def_list = prop_def.strip().split()
                field = prop_def_list[0].strip()
                if self.metadata_optional_fields[field]["type"] == "list":
                    value = prop_def_list[1:]
                else:
                    value = prop_def_list[1].strip()

                meta.update({field: value})

        return meta

    def extract_required_meta(self, line):
        meta = dict()

        for field in self.metadata_required_fields:
            if line.lower().startswith(f'#+{field}:'):
                field_type = self.metadata_required_fields[field]["type"]
                field_name = self.metadata_required_fields[field]["converts_to"]
                if field_type == "list":
                    value = line.split(":")[1].split(",")
                else:
                    value = line.split(":")[1]
                meta = {field_name: value}
                break

        return meta

    def convert_code(self, line):
        '''
        Translates a single line of a code block in orgmode syntax to markdown
        syntax.
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
        Translates a single line of an 'example' block in orgmode syntax
        to markdown syntax
        '''
        if "#+begin_example" in line.lower() or "#+end_example" in line.lower() or "#+results" in line.lower():
            return None

        return "    " + line.strip()

    def convert_result(self, line):
        if "#+results" in line.lower():
            return None

        return "    " + re.sub("^:", "", line.strip())

    def write_kp(self, new_lines, metadata):
        # Metadata header
        metadata_yml = dict_to_yaml(metadata)
        metadata_str = f'---\n{metadata_yml}\n---'

        body = metadata_str + "\n".join(new_lines)

        self.kp.write(body)
