# ResearchAPI

- REST: `/v1/*` (si exportas routers en `api/fecade.py`)
- GraphQL: `/graphql`
- Health: `/health`

## Desarrollo
- Run: `uvicorn researchapi.app:app --reload`
- Tests: `pytest`
- Cobertura: `pytest --cov=researchapi`

## Estructura
- `adapters`: clientes externos (arxiv/ieee/springer/cambridge)
- `api`: REST routers
- `bgraphql`: schema/resolvers
- `repository`: orquesta casos de uso/IO
- `search_strategies`: estrategias de búsqueda
