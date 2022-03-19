import yaml

def read_yaml(filename):
    with open(filename) as f:
        content = yaml.safe_load(f)
    return content

def read_binary(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content
