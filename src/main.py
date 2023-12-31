# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from bgraphql.resolvers import Query
from bgraphql.routes import router as api_router
import strawberry

# Carga las variables de entorno del archivo .env
load_dotenv()

# GraphQL part
schema = strawberry.Schema(query=Query)
graphql_app = GraphQL(schema)

app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "Hello, World!"}

# Routes for GraphQL
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

# Routes for REST
app.include_router(api_router)
