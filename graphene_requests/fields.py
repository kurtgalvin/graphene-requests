from graphene import Field, List


class RequestsField(Field):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields


class RequestsList(List):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields


class SelectionSet:
    __slots__ = ('selections',)

    def __init__(self, selections):
        assert isinstance(selections, (list, tuple)), "selections must be of type list or tuple"
        for i in selections:
            assert isinstance(i, Selection), f"{i} must be of type Selection"
        self.selections = selections

    def append(self, selection):
        '''update `SelectionSet` with a single `Selection` value
        '''
        assert isinstance(selection, Selection), "selection must be of type Selection"
        if not selection in self.selections:
            self.selections.append(selection)
        else:
            print("nope")

    def __iter__(self):
        return iter(self.selections)

    def __bool__(self):
        return bool(len(self.selections))

    def __repr__(self):
        return f"<SelectionSet selections={self.selections}>"


class Selection:
    __slots__ = ('field', 'args', 'sub_fields', 'type_', 'url')

    def __init__(self, field, args, sub_fields):
        self.type_ = None
        self.url = None
        assert isinstance(field, str), "field must be of type str"
        assert isinstance(args, dict), "args must be of type dict"
        assert isinstance(sub_fields, (list, tuple)), "sub_fields must be of type list or tuple"
        self.field = field
        self.args = args
        self.sub_fields = sub_fields

    def add_sub_field(self, selection):
        self.sub_fields.append(selection)
    
    def set_url(self, url):
        self.url = url

    def set_type(self, type_):
        self.type_ = type_

    def __eq__(self, other):
        return bool(
            self.field == other.field and
            self.args == other.args and
            self.sub_fields == other.sub_fields
        )

    def __repr__(self):
        return f"<Selection field={self.field} args={self.args} sub_fields={self.sub_fields} type_={self.type_}>"