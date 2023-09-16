import strawberry

@strawberry.type
class Article:
    title: str
    author: str
    publication_date: str
    # ... other fields