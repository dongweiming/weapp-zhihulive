# coding=utf-8
from datetime import datetime
from functools import wraps
from collections import OrderedDict

from marshmallow import ValidationError


def marshal(data, fields):
    schemas = [field() for field in fields]
    if isinstance(data, (list, tuple)):
        return [marshal(d, fields) for d in data]

    type = data.pop('type')
    for schema in schemas:
        if type in schema.__class__.__name__.lower():
            result, errors = schema.dump(data)
            if errors:
                for item in errors.items():
                    print('{}: {}'.format(*item))
            return result


class marshal_with(object):
    def __init__(self, fields):
        if not isinstance(fields, list):
            fields = [fields]
        self.fields = fields

    def __call__(self, f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            resp = await f(*args, **kwargs)
            return marshal(resp, self.fields)
        return wrapper


def str2date(string):
    if string is None:
        return None
    return datetime.strptime(string, '%Y-%m-%d').date()
