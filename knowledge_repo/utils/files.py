import os
import yaml


def read_text(filename):
    with open(filename, 'r') as f:
        return f.read()


def read_text_lines(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def read_yaml(filename):
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def read_binary(filename):
    with open(filename, 'rb') as f:
        return f.read()


def write_text(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def write_binary(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)


def get_path(__file__, directory, filename):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), directory, filename))
