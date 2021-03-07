from pathlib import Path

import setuptools
import toml
from jsonschema import validate

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

README_CONTENT_TYPES = {
    ".md": "text/markdown",
    ".rst": "text/x-rst",
    ".txt": "text/plain",
    "": "text/plain",
}


def setup(**attrs):
    if (pyproject_toml := Path("pyproject.toml")).exists():
        pyproject = toml.loads(pyproject_toml.read_text(encoding="utf-8"))
        validate(pyproject, SCHEMA)
        for k, v in pyproject.get("project", {}).items():
            attrs[k] = v
        for k, v in pyproject.get("tool", {}).get("pyproject-toml", {}).items():
            attrs[k] = v

    if "readme" in attrs:
        readme = attrs.pop("readme")
        if isinstance(readme, str):
            readme = Path(readme)
        elif "file" in readme:
            readme = Path(readme["file"])
        else:
            attrs["long_description"] = readme["text"]
        if isinstance(readme, Path):
            try:
                attrs["long_description_content_type"] = README_CONTENT_TYPES[readme.suffix]
            except KeyError:
                raise TypeError(f"Content type of {readme} is not supported")
            attrs["long_description"] = readme.read_text(encoding="utf-8")

    if "requires-python" in attrs:
        attrs["python_requires"] = attrs.pop("requires-python")

    if "license" in attrs:
        license = attrs.pop("license")
        if isinstance(license, str):
            raise NotImplementedError(
                "No PEP supports SPDX at 2021-03-07 when I write, see "
                "https://www.python.org/dev/peps/pep-0621/#id88"
            )
        if "text" in license:
            attrs["license"] = license["text"]
        elif "file" in license:
            attrs["license_file"] = license["file"]

    attrs["install_requires"] = attrs.pop("dependencies", None)
    
    setuptools.setup(**attrs)
