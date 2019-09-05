import requests
from string import Template
from graphene import ObjectType, String

from .utils import convert, selections_to_string, remove_fields, find_required_fields
from .requests import GrapheneRequests


class RequestsObjectType(ObjectType):
    '''
    Accepts standard graphql `SelectionSet` or dict as described below
    how to setup custom selections:
        selections = [
            {
                'name': 'profile',
                'selections': [
                    {
                        'name': 'id',
                        'selections': []
                    }
                ]
            },
            {
                'name': 'id',
                'selections': []
            }
        ]
        with recursion this prosses can be nested as deep as possible.

        TODO: add argument support eg: selections = [
            {
                'name': 'profile',
                'selections': [],
                'arguments': [
                    ???
                ]
            }
        ]
    '''
    __typename = String()
    def __init__(self, *args, **kwargs):
        if '__typename' in kwargs and kwargs['__typename']:
            self.__typename = kwargs.pop('__typename')
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls):
        _url = cls.Meta.url
        super().__init_subclass__()
        cls._meta.__dict__['url'] = _url

    @classmethod
    def from_service(cls, info, field_name=None, selections=None, selection_set=None, **kwargs):

        if selection_set:
            gr = GrapheneRequests(cls, selection_set)
        else:
            gr = GrapheneRequests.from_info(cls, info)
        gr.send(cls._meta.url)



        if not field_name:
            field_name = info.field_name
        if selections:
            assert isinstance(selections, list), "if specified, 'selections' must be a list"
            selections = selections_to_string(selections)
        else:
            selections = info.field_asts[0].selection_set.selections
            requireds = find_required_fields(cls, selections)
            selections = remove_fields(cls, selections)
            selections = selections_to_string(selections)

            if requireds:
                selections += ' '.join(requireds)

        template = Template('''{
            $field_name ($args) {
                $selections
            }
        }''')

        kwarg_str_list = []
        for k, v in kwargs.items():
            kwarg_str_list.append(f'{k}:')
            if isinstance(v, str):
                kwarg_str_list.append(f' "{v}" ')
            if isinstance(v, int):
                kwarg_str_list.append(f' {v} ')

        data = dict(
            field_name=field_name,
            args=''.join(kwarg_str_list),
            selections=selections
        )
        json = {'query': template.substitute(data)}
        r = requests.post(cls._meta.url, json=json)

        assert not 'errors' in  r.json(), r.json()['errors']
        name = cls._meta.name
        if not r.json()['data'][name]:
            return None
        if isinstance(r.json()['data'][name], list):
            return [cls(**convert(i)) for i in r.json()['data'][name]]
        return cls(**convert(r.json()['data'][name]))