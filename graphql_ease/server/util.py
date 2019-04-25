import json
from typing import Union, Dict, List

from graphql.execution import ExecutionResult

from .exceptions import HttpQueryError


__all__ = ["format_results", "load_json_body"]


def format_results(
    execution_results: List[ExecutionResult],
) -> Union[Dict, List[Dict]]:
    formatted_results = []

    for execution_result in execution_results:
        formatted_result = {"data": execution_result.data}
        if execution_result.errors:

            formatted_result["errors"] = []
            if execution_result.errors:
                for error in execution_result.errors:
                    formatted_result["errors"].append(error.formatted)

        formatted_results.append(formatted_result)

    if len(formatted_results) == 1:
        return formatted_results[0]

    return formatted_results


def load_json_body(data: str) -> Dict:
    try:
        return json.loads(data)
    except Exception:
        raise HttpQueryError(400, "POST body sent invalid JSON.")
