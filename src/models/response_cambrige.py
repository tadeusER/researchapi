from typing import List, Any
from datetime import datetime
import attr
from marshmallow import Schema, fields

@attr.dataclass
class LargeThumbnail:
    url: str

    def __init__(self, url: str) -> None:
        self.url = url

@attr.dataclass
class Asset:
    id: str
    mime_type: str
    file_name: str
    file_size_bytes: int
    small_thumbnail: LargeThumbnail
    medium_thumbnail: LargeThumbnail
    large_thumbnail: LargeThumbnail
    original: LargeThumbnail

    def __init__(self, id: str, mime_type: str, file_name: str, file_size_bytes: int, small_thumbnail: LargeThumbnail, medium_thumbnail: LargeThumbnail, large_thumbnail: LargeThumbnail, original: LargeThumbnail) -> None:
        self.id = id
        self.mime_type = mime_type
        self.file_name = file_name
        self.file_size_bytes = file_size_bytes
        self.small_thumbnail = small_thumbnail
        self.medium_thumbnail = medium_thumbnail
        self.large_thumbnail = large_thumbnail
        self.original = original

@attr.dataclass
class Institution:
    name: str
    country: str
    ror_id: str

    def __init__(self, name: str, country: str, ror_id: str) -> None:
        self.name = name
        self.country = country
        self.ror_id = ror_id

@attr.dataclass
class Author:
    orcid: str
    title: str
    first_name: str
    last_name: str
    institutions: List[Institution]

    def __init__(self, orcid: str, title: str, first_name: str, last_name: str, institutions: List[Institution]) -> None:
        self.orcid = orcid
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.institutions = institutions

@attr.dataclass
class License:
    id: str
    name: str
    description: str
    url: None

    def __init__(self, id: str, name: str, description: str, url: None) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.url = url

@attr.dataclass
class ContentType:
    id: str
    name: str

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

@attr.dataclass
class Sponsor:
    id: str
    url: str
    text: str
    asset: Asset

    def __init__(self, id: str, url: str, text: str, asset: Asset) -> None:
        self.id = id
        self.url = url
        self.text = text
        self.asset = asset

@attr.dataclass
class Event:
    id: str
    event_group: ContentType
    title: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_at: datetime
    banner_asset: Asset
    sponsors: List[Sponsor]
    url: None
    status: str

    def __init__(self, id: str, event_group: ContentType, title: str, description: str, location: str, start_date: datetime, end_date: datetime, created_at: datetime, updated_at: datetime, banner_asset: Asset, sponsors: List[Sponsor], url: None, status: str) -> None:
        self.id = id
        self.event_group = event_group
        self.title = title
        self.description = description
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.banner_asset = banner_asset
        self.sponsors = sponsors
        self.url = url
        self.status = status

@attr.dataclass
class Funder:
    funder_id: str
    name: str
    grant_number: str
    url: None
    title: None

    def __init__(self, funder_id: str, name: str, grant_number: str, url: None, title: None) -> None:
        self.funder_id = funder_id
        self.name = name
        self.grant_number = grant_number
        self.url = url
        self.title = title

@attr.dataclass
class Metric:
    description: str
    value: int

    def __init__(self, description: str, value: int) -> None:
        self.description = description
        self.value = value

@attr.dataclass
class VersionRef:
    version: int
    item_id: str
    legacy_id: None

    def __init__(self, version: int, item_id: str, legacy_id: None) -> None:
        self.version = version
        self.item_id = item_id
        self.legacy_id = legacy_id

@attr.dataclass
class Item:
    id: str
    doi: str
    vor: None
    title: str
    abstract: str
    content_type: ContentType
    categories: List[License]
    subject: License
    event: Event
    status: str
    status_date: datetime
    funders: List[Funder]
    authors: List[Author]
    metrics: List[Metric]
    version: int
    version_refs: List[VersionRef]
    submitted_date: datetime
    published_date: datetime
    approved_date: datetime
    keywords: List[str]
    has_competing_interests: bool
    competing_interests_declaration: None
    gained_ethics_approval: str
    supp_items: List[Any]
    asset: Asset
    license: License
    web_links: List[Any]
    origin: str
    terms_acceptance: bool
    version_note: str
    latest_comments: List[Any]
    comments_count: int
    is_latest_version: bool
    legacy_id: None

    def __init__(self, id: str, doi: str, vor: None, title: str, abstract: str, content_type: ContentType, categories: List[License], subject: License, event: Event, status: str, status_date: datetime, funders: List[Funder], authors: List[Author], metrics: List[Metric], version: int, version_refs: List[VersionRef], submitted_date: datetime, published_date: datetime, approved_date: datetime, keywords: List[str], has_competing_interests: bool, competing_interests_declaration: None, gained_ethics_approval: str, supp_items: List[Any], asset: Asset, license: License, web_links: List[Any], origin: str, terms_acceptance: bool, version_note: str, latest_comments: List[Any], comments_count: int, is_latest_version: bool, legacy_id: None) -> None:
        self.id = id
        self.doi = doi
        self.vor = vor
        self.title = title
        self.abstract = abstract
        self.content_type = content_type
        self.categories = categories
        self.subject = subject
        self.event = event
        self.status = status
        self.status_date = status_date
        self.funders = funders
        self.authors = authors
        self.metrics = metrics
        self.version = version
        self.version_refs = version_refs
        self.submitted_date = submitted_date
        self.published_date = published_date
        self.approved_date = approved_date
        self.keywords = keywords
        self.has_competing_interests = has_competing_interests
        self.competing_interests_declaration = competing_interests_declaration
        self.gained_ethics_approval = gained_ethics_approval
        self.supp_items = supp_items
        self.asset = asset
        self.license = license
        self.web_links = web_links
        self.origin = origin
        self.terms_acceptance = terms_acceptance
        self.version_note = version_note
        self.latest_comments = latest_comments
        self.comments_count = comments_count
        self.is_latest_version = is_latest_version
        self.legacy_id = legacy_id

@attr.dataclass
class ItemHit:
    item: Item

    def __init__(self, item: Item) -> None:
        self.item = item

@attr.dataclass
class CambrigeResponse:
    total_count: int
    item_hits: List[ItemHit]

    def __init__(self, total_count: int, item_hits: List[ItemHit]) -> None:
        self.total_count = total_count
        self.item_hits = item_hits
class LargeThumbnailSchema(Schema):
    url = fields.Str()

class AssetSchema(Schema):
    id = fields.Str()
    mime_type = fields.Str()
    file_name = fields.Str()
    file_size_bytes = fields.Int()
    small_thumbnail = fields.Nested(LargeThumbnailSchema)
    medium_thumbnail = fields.Nested(LargeThumbnailSchema)
    large_thumbnail = fields.Nested(LargeThumbnailSchema)
    original = fields.Nested(LargeThumbnailSchema)

class InstitutionSchema(Schema):
    name = fields.Str()
    country = fields.Str()
    ror_id = fields.Str()

class AuthorSchema(Schema):
    orcid = fields.Str()
    title = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    institutions = fields.Nested(InstitutionSchema, many=True)

class LicenseSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    description = fields.Str()
    url = fields.Str(allow_none=True)

class ContentTypeSchema(Schema):
    id = fields.Str()
    name = fields.Str()

class SponsorSchema(Schema):
    id = fields.Str()
    url = fields.Str()
    text = fields.Str()
    asset = fields.Nested(AssetSchema)

class EventSchema(Schema):
    id = fields.Str()
    event_group = fields.Nested(ContentTypeSchema)
    title = fields.Str()
    description = fields.Str()
    location = fields.Str()
    start_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    end_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    updated_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    banner_asset = fields.Nested(AssetSchema)
    sponsors = fields.Nested(SponsorSchema, many=True)
    url = fields.Str(allow_none=True)
    status = fields.Str()

class FunderSchema(Schema):
    funder_id = fields.Str()
    name = fields.Str()
    grant_number = fields.Str()
    url = fields.Str(allow_none=True)
    title = fields.Str(allow_none=True)

class MetricSchema(Schema):
    description = fields.Str()
    value = fields.Int()

class VersionRefSchema(Schema):
    version = fields.Int()
    item_id = fields.Str()
    legacy_id = fields.Str(allow_none=True)

class ItemSchema(Schema):
    id = fields.Str()
    doi = fields.Str()
    vor = fields.Str(allow_none=True)
    title = fields.Str()
    abstract = fields.Str()
    content_type = fields.Nested(ContentTypeSchema)
    categories = fields.Nested(LicenseSchema, many=True)
    subject = fields.Nested(LicenseSchema)
    event = fields.Nested(EventSchema)
    status = fields.Str()
    status_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    funders = fields.Nested(FunderSchema, many=True)
    authors = fields.Nested(AuthorSchema, many=True)
    metrics = fields.Nested(MetricSchema, many=True)
    version = fields.Int()
    version_refs = fields.Nested(VersionRefSchema, many=True)
    submitted_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    published_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    approved_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    keywords = fields.List(fields.Str())
    has_competing_interests = fields.Bool()
    competing_interests_declaration = fields.Str(allow_none=True)
    gained_ethics_approval = fields.Str()
    supp_items = fields.Nested(Any, many=True)  # No se especifica el esquema ya que es de tipo Any
    asset = fields.Nested(AssetSchema)
    license = fields.Nested(LicenseSchema)
    web_links = fields.Nested(Any, many=True)  # No se especifica el esquema ya que es de tipo Any
    origin = fields.Str()
    terms_acceptance = fields.Bool()
    version_note = fields.Str()
    latest_comments = fields.Nested(Any, many=True)  # No se especifica el esquema ya que es de tipo Any
    comments_count = fields.Int()
    is_latest_version = fields.Bool()
    legacy_id = fields.Str(allow_none=True)

class ItemHitSchema(Schema):
    item = fields.Nested(ItemSchema)

class CambrigeResponseSchema(Schema):
    total_count = fields.Int()
    item_hits = fields.Nested(ItemHitSchema, many=True)