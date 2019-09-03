

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
        new_key = ''
        for i in k:
            new_key += f"_{i.lower()}" if i.isupper() else i
        result.setdefault(new_key, v)
    return result