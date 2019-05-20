from graphql import FragmentSpreadNode, ListValueNode


__all__ = ["get_node_arguments", "get_node_fields"]


def get_node_arguments(info, arguments):
    for argument in arguments:
        if isinstance(argument.value, ListValueNode):
            yield {
                "name": argument.name.value,
                "value": [value.value for value in argument.value.values],
            }
        else:
            yield {"name": argument.name.value, "value": argument.value.value}


def get_node_fields(info, ast, fragments):
    field_nodes = ast.selection_set.selections

    for field_node in field_nodes:
        field_name = field_node.name.value
        if isinstance(field_node, FragmentSpreadNode):
            for field in fragments[field_name].selection_set.selections:
                yield {
                    "field": field.name.value,
                    "arguments": get_node_arguments(info, field_node.arguments)
                    if field_node.arguments
                    else [],
                    "children": get_node_fields(info, field, fragments)
                    if hasattr(field, "selection_set") and field.selection_set
                    else [],
                }
            continue

        yield {
            "field": field_name,
            "arguments": get_node_arguments(info, field_node.arguments)
            if field_node.arguments
            else [],
            "children": get_node_fields(info, field_node, fragments)
            if field_node.selection_set
            else [],
        }
