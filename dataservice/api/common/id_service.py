import uuid
import random
import base32_crockford as b32


def uuid_generator():
    """
    Returns a stringified uuid of 36 characters
    """
    return str(uuid.uuid4())


def kf_id_generator():
    """
    Returns a (Crockford)[http://www.crockford.com/wrmg/base32.html] base 32
    encoded number up to 8 characters left padded with 0

    Ex:
    '0004PEDE'
    'D167JSHP'
    'ZZZZZZZZ'
    '00000000'
    """
    return '{0:0>8}'.format(b32.encode(random.randint(0, 32**8-1)))
