from __future__ import annotations

import inspect
import re
from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints


_TOOL_REGISTRY: dict[str, dict] = {}


_PYTHON_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    dict: "object",
}


_FIELD_RE = re.compile(
    r"^:(\w+)(?:\s+(\w+))?:\s*(.*)$"
)


def _parse_docstring(
    doc: str | None,
) -> tuple[str, dict[str, str]]:
    """
    Parse a tool docstring.

    Returns:
        summary: The main description of the tool.
        parameter_descriptions: Mapping of parameter name to description.
    """

    if not doc:
        return "", {}

    lines = [
        line.strip()
        for line in inspect.cleandoc(doc).splitlines()
    ]

    summary_lines = []
    parameter_descriptions = {}

    for line in lines:
        match = _FIELD_RE.match(line)

        if match:
            parameter_name = match.group(1)
            description = match.group(3)

            parameter_descriptions[parameter_name] = description
        elif line:
            summary_lines.append(line)

    summary = " ".join(summary_lines)

    return summary, parameter_descriptions


def _python_type_to_json_schema(annotation):
    """
    Convert a Python type annotation into a JSON schema.
    """

    origin = get_origin(annotation)

    # Handles:
    #   str | None
    #   int | None
    #   Optional[str]
    #   Optional[int]
    if origin in (UnionType, Union):
        args = get_args(annotation)

        if type(None) in args:
            non_none_types = [
                arg
                for arg in args
                if arg is not type(None)
            ]

            if len(non_none_types) == 1:
                actual_type = non_none_types[0]

                json_type = _PYTHON_TO_JSON_TYPE.get(
                    actual_type,
                    "string",
                )

                return {
                    "type": [json_type, "null"]
                }

    # Normal types:
    #   str
    #   int
    #   float
    #   bool
    #   dict
    return {
        "type": _PYTHON_TO_JSON_TYPE.get(
            annotation,
            "string",
        )
    }


def llm_tool():
    """
    Decorator used to register a Python function as an LLM tool.

    The decorated function must have `session` as its first
    parameter. `session` is internal application state and is
    therefore excluded from the LLM-facing tool schema.
    """

    def decorator(func):
        signature = inspect.signature(func)

        type_hints = get_type_hints(func)

        summary, parameter_descriptions = _parse_docstring(
            func.__doc__
        )

        properties = {}
        required = []

        for parameter_name, parameter in signature.parameters.items():

            # session is internal application state.
            # The LLM must never see or provide it.
            if parameter_name == "session":
                continue

            annotation = type_hints.get(
                parameter_name,
                str,
            )

            parameter_schema = _python_type_to_json_schema(
                annotation
            )

            description = parameter_descriptions.get(
                parameter_name
            )

            if description:
                parameter_schema["description"] = description

            properties[parameter_name] = parameter_schema

            # Parameters without a default value are required.
            if parameter.default is inspect.Parameter.empty:
                required.append(parameter_name)

        parameters_schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            parameters_schema["required"] = required

        _TOOL_REGISTRY[func.__name__] = {
            "schema": {
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": summary,
                    "parameters": parameters_schema,
                },
            },
            "func": func,
        }

        return func

    return decorator


def get_tool_definitions() -> list[dict]:
    """
    Return all registered tools in LLM-compatible format.
    """

    return [
        entry["schema"]
        for entry in _TOOL_REGISTRY.values()
    ]


def call_tool(
    name: str,
    session: dict,
    arguments: dict,
) -> dict:
    """
    Execute a registered tool.

    The session is supplied by the application and is never
    controlled by the LLM.
    """

    entry = _TOOL_REGISTRY.get(name)

    if entry is None:
        return {
            "status": "error",
            "message": f"Unknown tool: {name}",
        }

    try:
        return entry["func"](
            session,
            **arguments,
        )

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }