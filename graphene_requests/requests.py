import requests

from .utils import _convert
from .fields import FieldSet, RequestsField, RequestsList


class GrapheneRequests:
    __slots__ = ('query', 'json')

    def __init__(self, class_, query):
        new_query = []
        for set_ in query:
            required = []
            new_query.append(FieldSet(set_.field, set_.args, []))
            for i in set_.sub_fields:
                obj = class_.__dict__[_convert(i.field)]
                if isinstance(obj, (RequestsField, RequestsList)):
                    for field in obj.required_fields:
                        required.append(FieldSet(field, {}, []))
                else:
                    if not i in new_query[-1].sub_fields:
                        new_query[-1].add_sub_field(i)
            for required_field in required:
                if not required_field in new_query[-1].sub_fields:
                    new_query[-1].add_sub_field(required_field)
        self.query = new_query

    def send(self, url):
        def to_string(obj): # recursive
            str_ = f'{obj.field} '
            args = ''
            for k, v in obj.args.items():
                args += f'{k}: "{v}" ' if isinstance(v, str) else f'{k}: {v} '
            if args:
                str_ += f'({args})'
            sub_fields = ''
            for sub_field in obj.sub_fields:
                sub_fields += to_string(sub_field)
            if sub_fields:
                str_ += f' {{{sub_fields}}} '
            return str_

        string = ''
        for i in self.query:
            string += to_string(i)
        json = {'query': f"{{{string}}}"}
        r = requests.post(url, json=json)
        assert not 'errors' in  r.json(), r.json()['errors']
        self.json = r.json()
        return self