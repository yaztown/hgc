'''
Created on Wednesday 06/03/2019

@author: yaztown
'''

from .myjson import MyJSONEncoder, MyJSONDecoder
from .hgc_json import HGCJSONEncoder

import json

def dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=HGCJSONEncoder, indent=None, separators=None,
        default=None, sort_keys=False, **kw):
    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
        allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
        default=default, sort_keys=sort_keys, **kw)

def loads(s, *, encoding=None, cls=None, object_hook=None, parse_float=None,
        parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
    return json.loads(s, encoding=encoding, cls=MyJSONDecoder, object_hook=object_hook, parse_float=parse_float,
        parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)

__all__ = ['MyJSONEncoder', 'MyJSONDecoder', 'HGCJSONEncoder', 'dumps', 'loads']