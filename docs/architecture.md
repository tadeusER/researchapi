# Arquitectura

- App factory: `researchapi.app.create_app()`
- Capas: API (REST/GraphQL) → Repository → Adapters
- Config: `config/base_config.py` + `pydantic-settings` (recomendado)
- Tests:
  - Unit: lógica pura con mocks
  - Integración: `TestClient` a la app
  - Red: `respx` para httpx
