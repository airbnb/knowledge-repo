import yaml


def read_text(filename):
    with open(filename, 'r') as f:
        content = f.read()
        return content


def read_text_lines(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return lines


def read_yaml(filename):
    with open(filename, 'r') as f:
        content = yaml.safe_load(f)
        return content


def read_binary(filename):
    with open(filename, 'rb') as f:
        content = f.read()
        return content


def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
