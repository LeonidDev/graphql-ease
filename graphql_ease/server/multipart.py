from typing import Union, Dict, List, IO

from .exceptions import HttpQueryError


__all__ = ["place_files_in_operations"]


def add_file_to_operations(
    operations: Union[Dict, List[Dict]], file: IO, path: List[str]
) -> None:
    if not path:
        if operations is not None:
            raise HttpQueryError(
                status=400, message="Path in map does not lead to a null value."
            )
        return file

    elif isinstance(operations, dict):
        key = path[0]
        operations[key] = add_file_to_operations(operations[key], file, path[1:])

    elif isinstance(operations, list):
        index = int(path[0])
        operations[index] = add_file_to_operations(operations[index], file, path[1:])

    else:
        raise HttpQueryError(
            status=400, message="Operations must be in JSON data structure."
        )

    return operations


def place_files_in_operations(
    operations: Union[Dict, List[Dict]],
    files_map: Dict[str, List[str]],
    files: Dict[str, IO],
) -> None:
    path_to_key_iter = (
        (value.split("."), key) for key, values in files_map.items() for value in values
    )

    for path, key in path_to_key_iter:
        add_file_to_operations(operations, files[key], path)
