import requests
from string import Template
from graphene import ObjectType, String

from .utils import convert, selections_to_string, remove_fields, find_required_fields
from .requests import GrapheneRequests
from .fields import FieldSet


class RequestsObjectType(ObjectType):
    def __init__(self, *args, **kwargs):
        if '__typename' in kwargs and kwargs['__typename']:
            self.__dict__['__typename'] = kwargs.pop('__typename')
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls):
        required = {'field_name', 'url'}
        meta_dict = {}
        for i in required:
            assert i in cls.Meta.__dict__, f"{i} is required in `Meta` within `RequestsObjectType`"
            meta_dict[i] = cls.Meta.__dict__[i]
        super().__init_subclass__()
        cls._meta.__dict__.update(meta_dict)
        setattr(cls, '__typename', String())

    @classmethod
    def from_service(cls, info=None, query=None):
        if info:
            query = FieldSet.from_info(info)
        gr = GrapheneRequests(cls, query)
        gr.send(cls._meta.url)

        name = cls._meta.field_name
        if isinstance(gr.json['data'][name], list):
            return [cls(**convert(i)) for i in gr.json['data'][name]]
        return cls(**convert(gr.json['data'][name]))