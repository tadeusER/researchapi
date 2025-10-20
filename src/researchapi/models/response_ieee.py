from typing import List
import attr
from marshmallow import EXCLUDE, Schema, fields, post_load

@attr.s
class AuthorAffiliations:
    authorAffiliation = attr.ib(type=List[str])

class AuthorAffiliationsSchema(Schema):
    authorAffiliation = fields.List(fields.Str())

    @post_load
    def make_object(self, data, **kwargs):
        return AuthorAffiliations(**data)

@attr.s
class Author:
    affiliation = attr.ib(type=str)
    authorUrl = attr.ib(type=str)
    id = attr.ib(type=int)
    full_name = attr.ib(type=str)
    author_order = attr.ib(type=int)
    authorAffiliations = attr.ib(type=AuthorAffiliations)

class AuthorSchema(Schema):
    affiliation = fields.Str()
    authorUrl = fields.Str()
    id = fields.Int()
    full_name = fields.Str(data_key="full_name")
    author_order = fields.Int(data_key="author_order")
    authorAffiliations = fields.Nested(AuthorAffiliationsSchema)

    @post_load
    def make_object(self, data, **kwargs):
        return Author(**data)

@attr.s
class Authors:
    authors = attr.ib(type=List[Author])

class AuthorsSchema(Schema):
    authors = fields.Nested(AuthorSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return Authors(**data)

@attr.s
class IeeeTerms:
    terms = attr.ib(type=List[str])

class IeeeTermsSchema(Schema):
    terms = fields.List(fields.Str())

    @post_load
    def make_object(self, data, **kwargs):
        return IeeeTerms(**data)

@attr.s
class AuthorTerms:
    terms = attr.ib(type=List[str])

class AuthorTermsSchema(Schema):
    terms = fields.List(fields.Str())

    @post_load
    def make_object(self, data, **kwargs):
        return AuthorTerms(**data)

@attr.s
class IndexTerms:
    ieee_terms = attr.ib(type=IeeeTerms)
    author_terms = attr.ib(type=AuthorTerms)

class IndexTermsSchema(Schema):
    ieee_terms = fields.Nested(IeeeTermsSchema, data_key="ieee_terms")
    author_terms = fields.Nested(AuthorTermsSchema, data_key="author_terms")

    @post_load
    def make_object(self, data, **kwargs):
        return IndexTerms(**data)

@attr.s
class IsbnFormat:
    format = attr.ib(type=str)
    value = attr.ib(type=str)
    isbnType = attr.ib(type=str)

class IsbnFormatSchema(Schema):
    format = fields.Str()
    value = fields.Str()
    isbnType = fields.Str(data_key="isbnType")

    @post_load
    def make_object(self, data, **kwargs):
        return IsbnFormat(**data)

@attr.s
class IsbnFormats:
    isbns = attr.ib(type=List[IsbnFormat])

class IsbnFormatsSchema(Schema):
    isbns = fields.Nested(IsbnFormatSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return IsbnFormats(**data)

# Similarmente para las clases Article y ResponseIEEE...

@attr.s
class Article:
    doi = attr.ib(type=str)
    title = attr.ib(type=str)
    publisher = attr.ib(type=str)
    isbn = attr.ib(type=str)
    issn = attr.ib(type=str)
    partnum = attr.ib(type=str)
    rank = attr.ib(type=int)
    authors = attr.ib(type=Authors)
    access_type = attr.ib(type=str)
    content_type = attr.ib(type=str)
    abstract = attr.ib(type=str)
    article_number = attr.ib(type=str)
    pdf_url = attr.ib(type=str)
    html_url = attr.ib(type=str)
    abstract_url = attr.ib(type=str)
    publication_title = attr.ib(type=str)
    conference_location = attr.ib(type=str)
    conference_dates = attr.ib(type=str)
    publication_number = attr.ib(type=int)
    is_number = attr.ib(type=int)
    publication_year = attr.ib(type=int)
    publication_date = attr.ib(type=str)
    start_page = attr.ib(type=str)
    end_page = attr.ib(type=str)
    citing_paper_count = attr.ib(type=int)
    citing_patent_count = attr.ib(type=int)
    download_count = attr.ib(type=int)
    insert_date = attr.ib(type=str)
    index_terms = attr.ib(type=IndexTerms)
    isbn_formats = attr.ib(type=IsbnFormats)

class ArticleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    doi = fields.Str()
    title = fields.Str()
    publisher = fields.Str()
    isbn = fields.Str()
    issn = fields.Str()
    partnum = fields.Str()
    rank = fields.Int()
    authors = fields.Nested(AuthorsSchema)
    access_type = fields.Str(data_key="access_type")
    content_type = fields.Str(data_key="content_type")
    abstract = fields.Str()
    article_number = fields.Str(data_key="article_number")
    pdf_url = fields.Str(data_key="pdf_url")
    html_url = fields.Str(data_key="html_url")
    abstract_url = fields.Str(data_key="abstract_url")
    publication_title = fields.Str(data_key="publication_title")
    conference_location = fields.Str(data_key="conference_location")
    conference_dates = fields.Str(data_key="conference_dates")
    publication_number = fields.Int(data_key="publication_number")
    is_number = fields.Int(data_key="is_number")
    publication_year = fields.Int(data_key="publication_year")
    publication_date = fields.Str(data_key="publication_date")
    start_page = fields.Str(data_key="start_page")
    end_page = fields.Str(data_key="end_page")
    citing_paper_count = fields.Int(data_key="citing_paper_count")
    citing_patent_count = fields.Int(data_key="citing_patent_count")
    download_count = fields.Int(data_key="download_count")
    insert_date = fields.Str(data_key="insert_date")
    index_terms = fields.Nested(IndexTermsSchema, data_key="index_terms")
    isbn_formats = fields.Nested(IsbnFormatsSchema, data_key="isbn_formats")

    @post_load
    def make_object(self, data, **kwargs):
        return Article(**data)

@attr.s
class ResponseIEEE:
    total_records = attr.ib(type=int)
    total_searched = attr.ib(type=int)
    articles = attr.ib(type=List[Article])

class ResponseIEEESchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total_records = fields.Int(data_key="total_records")
    total_searched = fields.Int(data_key="total_searched")
    articles = fields.Nested(ArticleSchema, many=True)

    @post_load
    def make_object(self, data, **kwargs):
        return ResponseIEEE(**data)
