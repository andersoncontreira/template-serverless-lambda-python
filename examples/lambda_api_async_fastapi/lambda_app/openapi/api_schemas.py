from marshmallow import Schema, fields

from lambda_app.enums.messages import MessagesEnum
from lambda_app.http_resources.request_control import Pagination
from lambda_app.openapi.schemas import DeletionSchema, RequestControlSchema, MetaSchema, LinkSchema


class EventSchema(Schema):
    type = fields.Str()
    data = fields.Dict()
    date = fields.DateTime(example="2021-05-03T19:41:36.315842-03:00")
    hash = fields.Str(example="406cce9743906f7b8d7dd5d5c5d8c95d820eeefd72a3a554a4a726d022d8fa19")


class OcorenSchema(Schema):
    chavenfe = fields.Str(example="32210206107255000134550010001712551245826554")
    ocor = fields.Str(example="MOTIVO DO CANCELAMENTO")
    origem = fields.Str(example="SAC/EAGLE")
    pedido = fields.Str(example="Z1223321")


class ProductSchema(Schema):
    sku = fields.Int(example=657705)
    quantity = fields.Int(example=1)


class EventCreateRequest(OcorenSchema):
    pass

class EventUpdateRequest(EventCreateRequest):
    pass


class EventListResponseSchema(Schema):
    data = fields.List(fields.Nested(EventSchema))
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventGetResponseSchema(Schema):
    data = fields.Nested(EventSchema)
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventCreateResponseSchema(Schema):
    result = fields.Bool(example=True)
    event_hash = fields.Str(example="c82bf3ee20dd2f4ae7109e52d313a3190f1a85ba3362c54d3eb6257bd0c4d69d")
    code = fields.Int(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.code)
    label = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.label)
    message = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.message)
    params = fields.List(fields.Str())


class EventCreateErrorResponseSchema(Schema):
    result = fields.Bool(example=False)
    event_hash = fields.Str(example=None)
    code = fields.Int(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.code)
    label = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.label)
    message = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.message)
    params = fields.List(fields.Str())


class EventUpdateResponseSchema(EventGetResponseSchema):
    pass


class EventDeleteResponseSchema(EventGetResponseSchema):
    data = fields.Nested(DeletionSchema)
