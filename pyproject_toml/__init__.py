from . import build_system, project, tool


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "build-system": build_system.__schema__,
        "project": project.__schema__,
        "tool": tool.__schema__,
    },
}
