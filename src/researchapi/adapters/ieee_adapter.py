import json
import time
import urllib.request
from typing import List, Optional, Dict

from marshmallow import ValidationError
from adapters.base_adapter import BaseAdapter
from models.article import Article
from models.response_ieee import ResponseIEEE, ResponseIEEESchema

class XPloreIEEE(BaseAdapter):
    BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles?"
    MAX_RESULTS = 20
    VALID_PARAMETERS = [
        "abstract", "affiliation", "article_number", "article_title", "author",
        "d-au", "doi", "d-publisher", "d-pubtype", "d-year", "end_date",
        "facet", "index_terms", "isbn", "issn", "is_number", "meta_data",
        "publication_title", "publication_year", "querytext", "start_date",
        "thesaurus_terms"
    ]
    VALID_FILTERS = {
        "content_type": [
            "Books", "Conferences", "Courses", "Early Access", "Journals", 
            "Journals,Magazines", "Magazines", "Standards"
        ],
        "end_year": None,  # To be validated for number
        "open_access": ["True", "False"],
        "publication_number": None,  # To be validated for number
        "publisher": [
            "Alcatel-Lucent", "AGU", "BIAI", "CSEE", "IBM", "IEEE", "IET", 
            "MITP", "Morgan & Claypool", "SMPTE", "TUP", "VDE"
        ],
        "start_year": None  # To be validated for number
    }
    VALID_SORTING_PAGING = {
        "max_records": (1, 200),  # Range for max_records
        "sort_field": ["article_number", "article_title", "publication_title"],
        "sort_order": ["asc", "desc"],
        "start_record": None  # To be validated for number
    }
    def __init__(self, token: str = "", base_params: dict = None):
        super().__init__(token, base_params)
        self.base_params = {
            "querytext": None,
        }
        self.reset_parameters()
    def _validate_parameters(self, params: dict) -> bool:
        if "article_number" in params and len(params) > 1:
            return False
        # Add other validation checks as necessary
        return True
    def _validate_filters(self, filters: dict) -> bool:
        for key, value in filters.items():
            valid_values = self.VALID_FILTERS.get(key, None)
            if valid_values is None:
                continue
            if value not in valid_values:
                return False
        return True
    def _validate_sorting_paging(self, sort_paging: dict) -> bool:
        for key, value in sort_paging.items():
            valid_values = self.VALID_SORTING_PAGING.get(key, None)
            
            if key == "max_records":
                if not (self.VALID_SORTING_PAGING["max_records"][0] <= value <= self.VALID_SORTING_PAGING["max_records"][1]):
                    return False
            elif valid_values is None:
                continue
            elif isinstance(valid_values, list) and value not in valid_values:
                return False
        return True
    def get_article(self, article_id: str):
        pass
    def map_to_article_from_ieee(self, response_data: ResponseIEEE) -> List[Article]:
        articles = []

        if not response_data or not response_data.articles:
            self.logger.warning("The provided ResponseIEEE object is empty or has no articles.")
            return articles

        for article_data in response_data.articles:
            try:
                article = Article.from_ieee_article(article_data)
                articles.append(article)
            except Exception as e:
                # Log the exception and continue processing the remaining items
                self.logger.error(f"Error mapping IEEE Article (DOI: {article_data.doi}) to Article: {str(e)}")

        self.logger.info(f"Successfully mapped {len(articles)} out of {len(response_data.articles)} IEEE Articles to Articles.")

        return articles

    def search(self, query: str)->ResponseIEEE:
        self.parameters["querytext"] = query
        response_data = self.execute_search()
        self.reset_parameters()
        schema = ResponseIEEESchema()
        try:
            ieee_response = schema.load(response_data)
            self.logger.info(f"type ieee_response: {type(ieee_response)}")
            return ieee_response
        except ValidationError as e:
            self.logger.error(f"Error deserializando la respuesta: {e.messages}")
            raise ValueError("Error procesando la respuesta de la API.")
    def multiple_search(self, queries: List[str])->List[ResponseIEEE]:
        all_results = []

        for query in queries:
            term_results = self.search(query)
            all_results.extend(term_results)

        return all_results

