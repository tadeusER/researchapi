from fastapi import APIRouter

router = APIRouter()

@router.get("/article/{id}")
def get_article(id: int):
    # Similar to the previous point, but for REST
    article_data = get_article_by_id(id)
    return article_data