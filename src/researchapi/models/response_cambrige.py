from typing import List, Any
from datetime import datetime
import attr
from marshmallow import EXCLUDE, Schema, fields, post_load

# Modelos usando attrs
@attr.s
class Thumbnail:
    url = attr.ib(type=str, default="")

@attr.s
class Asset:
    id = attr.ib(type=str, default="")
    mimeType = attr.ib(type=str, default="")
    fileName = attr.ib(type=str, default="")
    fileSizeBytes = attr.ib(type=int, default=0)
    smallThumbnail = attr.ib(type=Thumbnail, default=Thumbnail())
    mediumThumbnail = attr.ib(type=Thumbnail, default=Thumbnail())
    largeThumbnail = attr.ib(type=Thumbnail, default=Thumbnail())
    original = attr.ib(type=Thumbnail, default=Thumbnail())

@attr.s
class Sponsor:
    id = attr.ib(type=str, default="")
    url = attr.ib(type=str, default="")
    text = attr.ib(type=str, default="")
    asset = attr.ib(type=Asset, default=Asset())

@attr.s
class Event:
    id = attr.ib(type=str, default="")
    eventGroup = attr.ib(type=dict, default=dict())
    title = attr.ib(type=str, default="")
    description = attr.ib(type=str, default="")
    location = attr.ib(type=str, default="")
    startDate = attr.ib(type=datetime, default=datetime.now())
    endDate = attr.ib(type=datetime, default=datetime.now())
    createdAt = attr.ib(type=datetime, default=datetime.now())
    updatedAt = attr.ib(type=datetime, default=datetime.now())
    bannerAsset = attr.ib(type=Asset, default=Asset())
    sponsors = attr.ib(type=List[Sponsor], default=[])

@attr.s
class ContentType:
    id = attr.ib(type=str, default="")
    name = attr.ib(type=str, default="")

@attr.s
class Category:
    id = attr.ib(type=str, default="")
    name = attr.ib(type=str, default="")
    description = attr.ib(type=str, default="")

@attr.s
class Institution:
    name = attr.ib(type=str, default="")
    country = attr.ib(type=str, default="")
    rorId = attr.ib(type=str, default="")

@attr.s
class Author:
    orcid = attr.ib(type=str, default="")
    title = attr.ib(type=str, default="")
    firstName = attr.ib(type=str, default="")
    lastName = attr.ib(type=str, default="")
    institutions = attr.ib(type=List[Institution], default=[])

@attr.s
class Metric:
    description = attr.ib(type=str, default="")
    value = attr.ib(type=int, default=0)

@attr.s
class License:
    id = attr.ib(type=str, default="")
    name = attr.ib(type=str, default="")
    description = attr.ib(type=str, default="")
    url = attr.ib(type=str, default=None)

@attr.s
class ItemHit:
    item = attr.ib(type=dict, default=dict())
    status = attr.ib(type=str, default="")
    statusDate = attr.ib(type=datetime, default=datetime.now())
    funders = attr.ib(type=List[dict], default=[])
    authors = attr.ib(type=List[Author], default=[])
    metrics = attr.ib(type=List[Metric], default=[])
    version = attr.ib(type=str, default="")
    submittedDate = attr.ib(type=datetime, default=datetime.now())
    publishedDate = attr.ib(type=datetime, default=datetime.now())
    approvedDate = attr.ib(type=datetime, default=datetime.now())
    keywords = attr.ib(type=List[str], default=[])
    asset = attr.ib(type=Asset, default=Asset())
    license = attr.ib(type=License, default=License())
    commentsCount = attr.ib(type=int, default=0)

@attr.s
class CambrigeResponse:
    totalCount = attr.ib(type=int, default=0)
    itemHits = attr.ib(type=List[ItemHit], default=[])

# Esquemas de Marshmallow

class ThumbnailSchema(Schema):
    url = fields.Str()

    @post_load
    def make_thumbnail(self, data, **kwargs):
        return Thumbnail(**data)
class AssetSchema(Schema):
    id = fields.Str()
    mimeType = fields.Str(data_key="mimeType")
    fileName = fields.Str(data_key="fileName")
    fileSizeBytes = fields.Int(data_key="fileSizeBytes")
    smallThumbnail = fields.Nested(ThumbnailSchema, data_key="smallThumbnail")
    mediumThumbnail = fields.Nested(ThumbnailSchema, data_key="mediumThumb")
    largeThumbnail = fields.Nested(ThumbnailSchema, data_key="largeThumb")
    original = fields.Nested(ThumbnailSchema)

    @post_load
    def make_asset(self, data, **kwargs):
        return Asset(**data)

class SponsorSchema(Schema):
    id = fields.Str()
    url = fields.Str()
    text = fields.Str()
    asset = fields.Nested(AssetSchema)

    @post_load
    def make_sponsor(self, data, **kwargs):
        return Sponsor(**data)

class EventSchema(Schema):
    id = fields.Str()
    eventGroup = fields.Dict(data_key="eventGroup")
    title = fields.Str()
    description = fields.Str()
    location = fields.Str()
    startDate = fields.DateTime(data_key="startDate")
    endDate = fields.DateTime(data_key="endDate")
    createdAt = fields.DateTime(data_key="createdAt")
    updatedAt = fields.DateTime(data_key="updatedAt")
    bannerAsset = fields.Nested(AssetSchema, data_key="bannerAsset")
    sponsors = fields.List(fields.Nested(SponsorSchema))

    @post_load
    def make_event(self, data, **kwargs):
        return Event(**data)

class ContentTypeSchema(Schema):
    id = fields.Str()
    name = fields.Str()

    @post_load
    def make_content_type(self, data, **kwargs):
        return ContentType(**data)
class CategorySchema(Schema):
    id = fields.Str()
    name = fields.Str()
    description = fields.Str()

    @post_load
    def make_category(self, data, **kwargs):
        return Category(**data)

class InstitutionSchema(Schema):
    name = fields.Str()
    country = fields.Str()
    rorId = fields.Str(data_key="rorId")
    @post_load
    def make_institution(self, data, **kwargs):
        return Institution(**data)

class AuthorSchema(Schema):
    orcid = fields.Str()
    title = fields.Str()
    firstName = fields.Str(data_key="firstName")
    lastName = fields.Str(data_key="lastName")
    institutions = fields.List(fields.Nested(InstitutionSchema))

    @post_load
    def make_author(self, data, **kwargs):
        return Author(**data)

class MetricSchema(Schema):
    description = fields.Str()
    value = fields.Int()

    @post_load
    def make_metric(self, data, **kwargs):
        return Metric(**data)

class LicenseSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    description = fields.Str()
    url = fields.Str()

    @post_load
    def make_license(self, data, **kwargs):
        return License(**data)

class ItemHitSchema(Schema):
    item = fields.Dict()
    status = fields.Str()
    statusDate = fields.DateTime(data_key="statusDate")
    funders = fields.List(fields.Dict)
    authors = fields.List(fields.Nested(AuthorSchema))
    metrics = fields.List(fields.Nested(MetricSchema))
    version = fields.Str()
    submittedDate = fields.DateTime(data_key="submittedDate")
    publishedDate = fields.DateTime(data_key="publishedDate")
    approvedDate = fields.DateTime(data_key="approvedDate")
    keywords = fields.List(fields.Str)
    asset = fields.Nested(AssetSchema)
    license = fields.Nested(LicenseSchema)
    commentsCount = fields.Int(data_key="commentsCount")

    @post_load
    def make_item_hit(self, data, **kwargs):
        return ItemHit(**data)
class CambrigeResponseSchema(Schema):
    totalCount = fields.Int(data_key="totalCount")
    itemHits = fields.List(fields.Nested(ItemHitSchema), data_key="itemHits")

    @post_load
    def make_cambrige_response(self, data, **kwargs):
        return CambrigeResponse(**data)

