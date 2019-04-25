from typing import Union, Dict, List, IO, cast, Awaitable
from collections import MutableMapping
from inspect import isawaitable

from graphql import graphql, graphql_sync
from graphql.type import GraphQLSchema
from graphql.execution import ExecutionResult

from .exceptions import HttpQueryError
from .multipart import place_files_in_operations


__all__ = ["graphql_server", "graphql_server_sync"]


async def graphql_server(
    schema: GraphQLSchema,
    data: Union[Dict, List[Dict]],
    map_data: Dict[str, List[str]] = None,
    files_data: Dict[str, IO] = None,
    batch_enabled: bool = False,
    upload_enabled: bool = False,
    **options,
) -> List[ExecutionResult]:
    _results = graphql_server_impl(
        graphql,
        schema,
        data,
        map_data,
        files_data,
        batch_enabled,
        upload_enabled,
        options,
    )
    results = []
    for result in _results:
        if isawaitable(result):
            result = await cast(Awaitable[ExecutionResult], result)
        results.append(result)
    return results


def graphql_server_sync(
    schema: GraphQLSchema,
    data: Union[Dict, List[Dict]],
    map_data: Dict[str, List[str]] = None,
    files_data: Dict[str, IO] = None,
    batch_enabled: bool = False,
    upload_enabled: bool = False,
    **options,
) -> List[ExecutionResult]:
    return graphql_server_impl(
        graphql_sync,
        schema,
        data,
        map_data,
        files_data,
        batch_enabled,
        upload_enabled,
        options,
    )


def graphql_server_impl(
    graphql_func,
    schema,
    data,
    map_data,
    files_data,
    batch_enabled,
    upload_enabled,
    options,
) -> Union[ExecutionResult, List[ExecutionResult]]:
    is_batch = isinstance(data, list)

    if not is_batch:
        if not isinstance(data, (dict, MutableMapping)):
            raise HttpQueryError(
                400, f"GraphQL params should be a dict. Received {data}."
            )
        data = [data]

    elif not batch_enabled:
        raise HttpQueryError(400, "Batch GraphQL requests are not enabled.")

    if not data:
        raise HttpQueryError(400, "Received an empty list in the batch request.")

    if upload_enabled and map_data and files_data:
        place_files_in_operations(data, map_data, files_data)

    results = []

    for param_data in data:
        query = param_data.get("query", "")
        variable_values = param_data.get("variables", {})
        operation_name = param_data.get("operationName", None)

        results.append(
            graphql_func(
                schema=schema,
                source=query,
                variable_values=variable_values,
                operation_name=operation_name,
                **options,
            )
        )

    return results
