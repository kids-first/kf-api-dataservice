import pkg_resources
from itertools import tee


def _get_version():
    return pkg_resources.get_distribution("kf-api-dataservice").version


def iterate_pairwise(iterable):
    """
    Iterate over an iterable in consecutive pairs
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
