__schema__ = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "patter": r"^([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9])$",
        },
        "version": {"type": "string"},
        "description": {"type": "string"},
        "readme": {
            "anyOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {"file": {"type": "string"}},
                    "required": ["file"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
            ]
        },
        "requires-python": {"type": "string"},
        "license": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {"file": {"type": "string"}},
                    "required": ["file"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
            ]
        },
        "authors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
            },
        },
        "maintainers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
            },
        },
        "keywords": {"type": "array", "items": {"type": "string"}},
        "classifiers": {"type": "array", "items": {"type": "string"}},
        "urls": {"type": "object"},
        "scripts": {"type": "object"},
        "gui-scripts": {"type": "object"},
        "entry-points": {"type": "object"},
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "optional-dependencies": {"type": "array", "items": {"type": "string"}},
        "dynamic": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "version"],
}
