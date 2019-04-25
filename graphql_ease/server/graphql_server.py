from typing import Optional

from .graphiql import format_graphiql


__all__ = ["GraphQLServer"]


class GraphQLServer(object):
    def __init__(
        self,
        schema,
        graphiql: bool = False,
        upload: bool = False,
        batch: bool = False,
        subscription: Optional[str] = "",
        context: Optional[dict] = {},
        **options,
    ):
        self.schema = schema
        self.graphiql = graphiql
        self.upload = upload
        self.batch = batch
        self.subscription = subscription
        self.context = context
        self.options = options

    @property
    def template(self):
        return format_graphiql(self.subscription)

    def flask_view(self, name):
        from .impl.flask import GraphQLView

        return GraphQLView.as_view(
            name,
            self.schema,
            self.graphiql,
            self.batch,
            self.upload,
            self.context,
            self.options,
            self.template,
        )

    def sanic_view(self):
        from .impl.sanic import GraphQLView

        return GraphQLView.as_view(
            self.schema,
            self.graphiql,
            self.batch,
            self.upload,
            self.context,
            self.options,
            self.template,
        )

    async def handle(self):
        raise NotImplementedError

    def sync_handle(self):
        raise NotImplementedError
