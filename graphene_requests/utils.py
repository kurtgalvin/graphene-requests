from .fields import RequestsField, RequestsList

def _convert(string):
    assert isinstance(string, str), "can only convert string"
    value = ''
    for i in string:
        value += f"_{i.lower()}" if i.isupper() else i
    return value

def find_required_fields(cls, selections):
    fields = []
    for i in selections:
        key = _convert(i.name.value)
        obj = cls.__dict__[key]
        if isinstance(obj, (RequestsField, RequestsList)) and obj.required_fields:
            fields.extend(obj.required_fields)
    return fields

def remove_fields(cls, selections):
    def parse(selection):
        key = _convert(selection.name.value)
        if isinstance(cls.__dict__[key], (RequestsField, RequestsList)):
            return False
        return True
    return list(filter(parse, selections))

def selections_to_string(selections):
    string=''
    for i in selections:
        if isinstance(i, dict):
            string += f" {i['name']} "
            assert not 'directives' in i, "directives not implemented"
            if 'arguments' in i and i['arguments']:
                parsed = [f"{x['key']}: {x['value']} " for x in i['arguments']]
                string += f"({''.join(parsed)})"
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
        new_key = _convert(k)
        result.setdefault(new_key, v)
    return result