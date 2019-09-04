from graphene import Field


class RequestsField(Field):
    def __init__(self, *args, **kwargs):
        required_fields = kwargs.pop('required_fields', None)
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields