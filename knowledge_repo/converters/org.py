import re

from ..converter import KnowledgePostConverter

class OrgConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
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
        "date_updated": {
            "type": "string",
            "converts_to": "updated_at"
        },
        "tldr": {
            "type": "string",
            "converts_to": "tldr"
        },
        "post_tags": {
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
        #TODO: Image support

        # These dict will let use the correct function for each line
        line_converters = {
            "src": self.convert_code,
            "text": self.convert_text,
            "example": self.convert_example
        }

        new_lines = []
        metadata = []
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
                metadata.extend(new_meta)

            if new_line is not None:
                new_lines.append(new_line)

        return self.write_kp(new_lines, metadata)

    def convert_text(self, line):
        #TODO: inline source
        #TODO: strikethrough

        new_line = line

        # Headers (Org: *Header)
        header_match = re.match("^(\*+)", new_line)
        if header_match:
            n_asts = len(header_match.group(1))
            new_line = re.sub("^(\*+)", "#"*n_asts, new_line)

        # Bold (Org: *bold*)
        reg = re.compile(r"[^\w]\*([^\*]+)\*[^\w]", re.U)
        bold_find = re.finditer(reg, new_line)
        for match in bold_find:
            bolded = match.group(1)
            new_line = new_line.replace("*{}*".format(bolded), "**{}**".format(bolded))

        # Italics (Org: /italic/)
        reg = re.compile("[^\w/]/([^/]+)/[^\w/]", re.U)
        italics_find = re.finditer(reg, new_line)
        for match in italics_find:
            italicized = match.group(1)
            new_line = new_line.replace("/{}/".format(italicized), "_{}_".format(italicized))

        # Hyperlinks (Org: [[link][desc]])
        reg = re.compile("\[\[([^\[\]]+)\]\[([^\[\]]+)\]\]")
        hlink_find = re.finditer(reg, new_line)
        for match in hlink_find:
            link, desc = match.groups()
            new_hlink = "[{}]({})".format(desc, link)
            new_line = new_line.replace("[[{}][{}]]".format(link, desc), new_hlink)

        return new_line.strip()

    def extract_meta(self, line):
        meta = None
        line = line.strip()
        for field in self.metadata_fields:
            if line.lower().startswith("#+{}:".format(field)):
                field_type = self.metadata_fields[field]["type"]
                field_name = self.metadata_fields[field]["converts_to"]

                # Add a single line to metadata YAML
                if field_type == "string":
                    value = line.split(":")[1].strip()
                    meta = ["{}: {}".format(field_name, value)]
                # Add multiple lines to metadata YAML
                elif field_type == "list":
                    values = line.split(":")[1].strip().split(",")
                    meta = ["{}:".format(field_name)]
                    for value in values:
                        meta.append("- {}".format(value))

                break
        return meta

    def convert_code(self, line):
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
        if "#+begin_example" in line.lower() or "#+end_example" in line.lower():
            return None

        return "    " + line.strip()

    def write_kp(self, new_lines, metadata):
        # Metadata header
        metadata_str = "---\n{}\n---".format("\n".join(metadata))

        body = metadata_str + "\n".join(new_lines)

        self.kp.write(body)
