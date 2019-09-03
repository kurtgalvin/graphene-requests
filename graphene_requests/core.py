import requests
from string import Template
from graphene import ObjectType

def selections_to_string(selections, string=''):
    '''
    This function accepts standard graphql `SelectionSet` or dict as described below
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
    for i in selections:
        if isinstance(i, dict):
            string += f" {i['name']} "
            assert not 'arguments' in i, "arguments not implemented"
            assert not 'directives' in i, "directives not implemented"
            if 'selections' in i and i['selections']:
                string += f"{{{selections_to_string(i['selections'])}}}"
        else:
            string += f" {i.name.value} "
            assert not i.arguments, "arguments not implemented"
            assert not i.directives, "directives not implemented"
            if i.selection_set:
                string += f"{{{selections_to_string(i.selection_set.selections)}}}"
    return string

def convert(obj):
    result={}
    for k, v in obj.items():
        new_key = ''
        for i in k:
            new_key += f"_{i.lower()}" if i.isupper() else i
        result.setdefault(new_key, v)
    return result


class RequestsObjectType(ObjectType):
    def __init_subclass__(cls):
        _url = cls.Meta.url
        super().__init_subclass__()
        cls._meta.__dict__['url'] = _url

    @classmethod
    def from_service(cls, info, field_name=None, selections=None, **kwargs):
        if not field_name:
            field_name = info.field_name
        if selections:
            assert isinstance(selections, list), "if specified, 'selections' must be a list"
            selections = selections_to_string(selections)
        else:
            selections = info.field_asts[0].selection_set.selections
            selections = selections_to_string(selections)

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
        if isinstance(r.json()['data'][name], list):
            return [cls(**convert(i)) for i in r.json()['data'][name]]
        return cls(**convert(r.json()['data'][name]))