from typing import List, Any
from datetime import datetime
import attr
from marshmallow import EXCLUDE, Schema, fields, post_load

@attr.s(auto_attribs=True)
class URL:
    format: str
    platform: str
    value: str

@attr.s(auto_attribs=True)
class Creator:
    creator: str
    ORCID: str = None 

@attr.s(auto_attribs=True)
class Chapter:
    content_type: str = attr.ib(metadata={"data_key": "contentType"})
    identifier: str
    language: str
    url: List[URL]
    title: str
    creators: List[Creator]
    publication_name: str = attr.ib(metadata={"data_key": "publicationName"})
    openaccess: str
    doi: str
    publisher: str
    publication_date: str = attr.ib(metadata={"data_key": "publicationDate"})
    publication_type: str = attr.ib(metadata={"data_key": "publicationType"})
    print_isbn: str = attr.ib(metadata={"data_key": "printIsbn"})
    electronic_isbn: str = attr.ib(metadata={"data_key": "electronicIsbn"})
    isbn: str
    genre: str
    copyright: str
    abstract: str
    subjects: List[str]

class URLSchema(Schema):
    format = fields.Str()
    platform = fields.Str()
    value = fields.Str()

class CreatorSchema(Schema):
    creator = fields.Str()
    ORCID = fields.Str(allow_none=True)

class ChapterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    contentType = fields.Str(attribute="content_type")
    identifier = fields.Str()
    language = fields.Str()
    url = fields.List(fields.Nested(URLSchema))
    title = fields.Str()
    creators = fields.List(fields.Nested(CreatorSchema))
    publicationName = fields.Str(attribute="publication_name")
    openaccess = fields.Str()
    doi = fields.Str()
    publisher = fields.Str()
    publicationDate = fields.Str(attribute="publication_date")
    publicationType = fields.Str(attribute="publication_type")
    printIsbn = fields.Str(attribute="print_isbn")
    electronicIsbn = fields.Str(attribute="electronic_isbn")
    isbn = fields.Str()
    genre = fields.Str()
    copyright = fields.Str()
    abstract = fields.Str()
    subjects = fields.List(fields.Str())

    @post_load
    def make_chapter(self, data, **kwargs):
        data['creators'] = [Creator(**item) for item in data.get('creators', [])]
        data['url'] = [URL(**item) for item in data.get('url', [])]

        return Chapter(**data)

@attr.s(auto_attribs=True)
class SpringerResponse:
    chapters: List[Chapter]

class SpringerResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    chapters = fields.List(fields.Nested(ChapterSchema))

    @post_load
    def make_springer_response(self, data, **kwargs):
        return SpringerResponse(**data)