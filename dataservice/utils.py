import json
import pkg_resources
from itertools import tee
from re import sub


def _get_version():
    return pkg_resources.get_distribution("kf-api-dataservice").version


def iterate_pairwise(iterable):
    """
    Iterate over an iterable in consecutive pairs
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def to_snake_case(camel_case_str):
    """
    Convert camel case string to snake case string

    Example: FooBarBaz converts to foo_bar_baz
    """
    s1 = sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_str)

    return sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def read_json(filepath):
    with open(filepath, 'r') as json_file:
        return json.load(json_file)


def write_json(data, filepath):
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4,
                  separators=(',', ':'))
