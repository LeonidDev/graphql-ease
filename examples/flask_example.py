from flask import Flask

from graphql_ease import (
    declarative_schema,
    Object,
    Field,
    String,
    Query,
    Argument,
    Int,
    ID,
)
from graphql_ease.server import GraphQLServer


roles = [{"name": "meow"}, {"name": "woof"}]

users = {
    1: {"id": 1, "name": "steve", "roles": []},
    2: {"id": 2, "name": "bob", "roles": roles},
}


schema = declarative_schema()


class User(Object, schema):
    id = Field(ID, required=True)
    name = Field(String, required=True)
    roles = Field("Role", many=True)

    @Query("User")
    @Argument("id", Int)
    def user(obj, info, id):
        return users.get(id)

    @Query("User", many=True)
    def users(obj, info):
        return users.values()


class Role(Object, schema):
    name = Field(String, required=True)

    @Query("Role", many=True)
    def roles(obj, info):
        return roles.values()


graphql_server = GraphQLServer(schema=schema.build(), graphiql=True)


app = Flask(__name__)
app.debug = True
app.add_url_rule(rule="/graphql", view_func=graphql_server.flask_view("graphql"))


if __name__ == "__main__":
    app.run()
