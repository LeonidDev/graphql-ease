from sanic.views import HTTPMethodView
from sanic.response import html, HTTPResponse, json

from ..server import graphql_server
from ..exceptions import HttpQueryError
from ..util import load_json_body, format_results


__all__ = ["GraphQLView"]


class GraphQLView(HTTPMethodView):
    methods = ["GET", "POST"]

    def __init__(self, schema, graphiql, batch, upload, context, options, template):
        self.schema = schema
        self.graphiql = graphiql
        self.batch = batch
        self.upload = upload
        self.context = context
        self.options = options
        self.template = template

    async def dispatch_request(self, request, *args, **kwargs):
        try:
            if request.method.lower() == "get":
                if self.graphiql:
                    return self.render_graphiql()
            else:
                data, map_data, files_data = self.parse_body(request)
                execution_results = await graphql_server(
                    schema=self.schema,
                    data=data,
                    map_data=map_data,
                    files_data=files_data,
                    batch_enabled=self.batch,
                    upload_enabled=self.upload,
                    context_value=self.context,
                    **self.options,
                )
                return json(format_results(execution_results))
        except HttpQueryError as error:
            return HTTPResponse(
                json(error.as_dict()),
                status=error.status,
                content_type="application/json",
            )

    def render_graphiql(self):
        return html(self.template)

    def parse_body(self, request):
        content_type = request.headers.get("Content-Type", "application/json")
        data, map_data, files_data = {}, {}, {}

        if content_type == "application/json":
            data = load_json_body(request.body.decode("utf8"))

        elif content_type == "multipart/form-data":
            data = request.form
            map_data = load_json_body(request.form.get("operations", "{}"))
            files_data = load_json_body(request.form.get("map", "{}"))

        return data, map_data, files_data
