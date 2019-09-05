import requests

from .utils import _convert
from .fields import SelectionSet, Selection, RequestsField, RequestsList


class GrapheneRequests:
    __slots__ = ('query',)

    def __init__(self, class_, selection_set):
        assert isinstance(selection_set, SelectionSet), "selection_set must be of type `SelectionSet`"

        # TODO: index to last self.query and keep appending aproved fields
        self.query = SelectionSet([])
        for set_ in selection_set:
            self.query.append(Selection(set_.field, set_.args, []))
            for i in set_.sub_fields:
                obj = class_.__dict__[_convert(i.field)]
                if isinstance(obj, (RequestsField, RequestsList)):
                    for field in obj.required_fields:
                        self.query.append(Selection(field, {}, []))
                else:
                    self.query.append(i)

    @classmethod
    def from_info(cls, class_, info):
        selection_set = SelectionSet([])

        def unpack(obj): # recursive
            field = obj.name.value
            args = {}
            for arg in obj.arguments:
                args[arg.name.value] = arg.value.value
            sub_fields=[]
            if obj.selection_set:
                for s in obj.selection_set.selections:
                    sub_fields.append(unpack(s))
            return Selection(field, args, sub_fields)

        for i in info.field_asts:
            selection_set.append(unpack(i))
        return cls(class_, selection_set)

    def send(self, url):
        def to_string(str_, obj):
            print(obj)
            return ''

        string = ''
        for i in self.query:
            string += to_string('', i)
        json = {'query': string}
        print(json)
        # r = requests.post(url, json=json)