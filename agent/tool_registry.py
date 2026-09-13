from __future__ import annotations

import inspect
import re
from typing import get_args, get_origin, get_type_hints

_TOOL_REGISTRY: dict[str, dict] = {}

_PYTHON_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    dict: "object",
}

_FIELD_RE = re.compile(r"^:(\w+)(?:\s+(\w+))?:\s*(.*)$")


def _parse_docstring(doc: str | None) -> tuple[str, dict[str, str]]:
    """Split a reST-style docstring into (summary, {param_name: description})."""
    if not doc:
        return "", {}
    lines = inspect.cleandoc(doc).splitlines()
    i = 0
    while i < len(lines) and not lines[i].lstrip().startswith(":"):
        i += 1
    summary = "\n".join(lines[:i]).strip()
    param_descriptions: dict[str, str] = {}
    current_param = None
    for line in lines[i:]:
        stripped = line.strip()
        if not stripped:
            continue

        match = _FIELD_RE.match(stripped)
        if match:
            field, name, text = match.groups()
            if field == "param" and name:
                current_param = name
                param_descriptions[name] = text.strip()
            else:
                current_param = None
        elif current_param:
            param_descriptions[current_param] += " " + stripped
    return summary, param_descriptions


def llm_tool():
    """Register a function as an LLM-callable tool."""

    def decorator(func):
        sig = inspect.signature(func)
        hints = get_type_hints(func)
        summary, param_docs = _parse_docstring(inspect.getdoc(func))
        properties = {}
        required = []
        for param in sig.parameters.values():
            # session is injected by our application,
            # so the LLM never sees it.
            if param.name == "session":
                continue
            py_type = hints.get(param.name, str)
            if get_origin(py_type) is list:
                args = get_args(py_type)
                item_type = args[0] if args else str
                schema = {
                    "type": "array",
                    "items": {
                        "type": _PYTHON_TO_JSON_TYPE.get(
                            item_type,
                            "string"
                        )
                    }
                }

            else:
                args = [a for a in get_args(py_type) if a is not type(None)]
                base_type = args[0] if args else py_type
                schema = {"type": _PYTHON_TO_JSON_TYPE.get(base_type, "string")}

            if param.name in param_docs:
                schema["description"] = param_docs[param.name]
            properties[param.name] = schema
            if param.default is inspect.Parameter.empty:
                required.append(param.name)

        parameters_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

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
    return [entry["schema"] for entry in _TOOL_REGISTRY.values()]


def call_tool(name: str, session: dict, arguments: dict) -> dict:

    entry = _TOOL_REGISTRY.get(name)

    if entry is None:
        return {"status": "error", "message": f"Unknown tool '{name}'."}

    return entry["func"](session, **arguments)