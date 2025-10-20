from typing import List, Optional, Dict, Any

from models.base_obj import BaseObject

class TitleDetail(BaseObject):
    def __init__(self, type: str, language: Optional[str], base: str, value: str):
        self.type = type
        self.language = language
        self.base = base
        self.value = value

class Author(BaseObject):
    def __init__(self, name: str):
        self.name = name

class Link(BaseObject):
    def __init__(self, href: str, rel: str, type: str, title: Optional[str] = None):
        self.href = href
        self.rel = rel
        self.type = type
        self.title = title

class Tag(BaseObject):
    def __init__(self, term: str, scheme: str, label: Optional[str]):
        self.term = term
        self.scheme = scheme
        self.label = label

class Entry(BaseObject):
    def __init__(self, 
                 id: str = "",
                 guidislink: bool = False,
                 link: str = "",
                 updated: str = "",
                 updated_parsed: List[int] = [],
                 published: str = "",
                 published_parsed: List[int] = [],
                 title: str = "",
                 title_detail: Dict[str, Any] = {},
                 summary: str = "",
                 summary_detail: Dict[str, Any] = {},
                 authors: List[Dict[str, Any]] = [],
                 author_detail: Dict[str, Any] = {},
                 author: str = "",
                 arxiv_doi: str = "",
                 links: List[Dict[str, Any]] = [],
                 arxiv_comment: str = "",
                 arxiv_primary_category: Dict[str, Any] = {},
                 tags: List[Dict[str, Any]] = []):
        
        self.id = id
        self.guidislink = guidislink
        self.link = link
        self.updated = updated
        self.updated_parsed = updated_parsed
        self.published = published
        self.published_parsed = published_parsed
        self.title = title
        self.title_detail = TitleDetail.from_dict(title_detail)
        self.summary = summary
        self.summary_detail = TitleDetail.from_dict(summary_detail)
        self.authors = [Author.from_dict(author_data) for author_data in authors]
        self.author_detail = Author.from_dict(author_detail)
        self.author = author
        self.arxiv_doi = arxiv_doi
        self.links = [Link.from_dict(link_data) for link_data in links]
        self.arxiv_comment = arxiv_comment
        self.arxiv_primary_category = Tag.from_dict(arxiv_primary_category)
        self.tags = [Tag.from_dict(tag_data) for tag_data in tags]


class Feed(BaseObject):
    def __init__(self, 
                 links: List[Link],
                 title: str,
                 title_detail: TitleDetail,
                 id: str,
                 guidislink: bool,
                 link: str,
                 updated: str,
                 updated_parsed: List[int],
                 opensearch_totalresults: str,
                 opensearch_startindex: str,
                 opensearch_itemsperpage: str):
        self.links = links
        self.title = title
        self.title_detail = title_detail
        self.id = id
        self.guidislink = guidislink
        self.link = link
        self.updated = updated
        self.updated_parsed = updated_parsed
        self.opensearch_totalresults = opensearch_totalresults
        self.opensearch_startindex = opensearch_startindex
        self.opensearch_itemsperpage = opensearch_itemsperpage

class ArxivResponse(BaseObject):
    def __init__(self, 
                 bozo: bool,
                 entries: List[Entry],
                 feed: Feed,
                 headers: Dict[str, Any],
                 encoding: str,
                 version: str,
                 namespaces: Dict[str, str]):
        self.bozo = bozo
        self.entries = entries
        self.feed = feed
        self.headers = headers
        self.encoding = encoding
        self.version = version
        self.namespaces = namespaces
