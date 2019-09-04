from graphene import Field, List


class RequestsField(Field):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields


class RequestsList(List):
    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = required_fields