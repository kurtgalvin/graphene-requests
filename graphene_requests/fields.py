from graphql.execution.base import ResolveInfo
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
        self.field = field
        self.args = args

        if isinstance(sub_fields, ResolveInfo):
            assert self.field == sub_fields.field_name, "`ResolveInfo` object must be used at the correct abstraction level"
            for i in sub_fields.field_asts:
                if i.name.value == self.field:
                    sub_fields = FieldSet.from_info(i.selection_set.selections)
                    break

        assert isinstance(sub_fields, (list, tuple)), "sub_fields must be of type list or tuple"
        self.sub_fields = sub_fields

    def add_sub_field(self, field):
        self.sub_fields.append(field)

    def add_sub_fields(self, fields):
        fields_to_add = []
        for i in fields:
            for x in self.sub_fields:
                if i.field != x.field:
                    fields_to_add.append(i)
        self.sub_fields.extend(fields_to_add)

    @classmethod
    def from_info(cls, obj):
        if isinstance(obj, ResolveInfo):
            return [cls.from_info(i) for i in obj.field_asts]
        if isinstance(obj, list):
            return [cls.from_info(i) for i in obj]
        
        field = obj.name.value
        args = {}
        for arg in obj.arguments:
            args[arg.name.value] = arg.value.value
        sub_fields=[]
        if obj.selection_set:
            for selection in obj.selection_set.selections:
                sub_fields.append(cls.from_info(selection))
        return cls(field, args, sub_fields)

    def __eq__(self, other):
        return bool(
            self.field == other.field and
            self.args == other.args and
            self.sub_fields == other.sub_fields 
        )

    def __repr__(self):
        return f"<FieldSet field={self.field} args={self.args} sub_fields={self.sub_fields}>"