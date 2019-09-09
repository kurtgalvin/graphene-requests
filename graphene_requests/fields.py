from graphene import Field, List


class RequestsField(Field):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields


class RequestsList(List):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields


class FieldSet:
    __slots__ = ('field', 'args', 'sub_fields')

    def __init__(self, field, args, sub_fields):
        assert isinstance(field, str), "field must be of type str"
        assert isinstance(args, dict), "args must be of type dict"
        assert isinstance(sub_fields, (list, tuple)), "sub_fields must be of type list or tuple"
        self.field = field
        self.args = args
        self.sub_fields = sub_fields

    def add_sub_field(self, field):
        self.sub_fields.append(field)

    def __eq__(self, other):
        return bool(
            self.field == other.field and
            self.args == other.args and
            self.sub_fields == other.sub_fields
        )

    def __repr__(self):
        return f"<Selection field={self.field} args={self.args} sub_fields={self.sub_fields}>"