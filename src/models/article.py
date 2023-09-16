import strawberry

@strawberry.type
class Article:
    id: str
    title: str
    # ... other fields