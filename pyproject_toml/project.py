"""Project metadata.
https://peps.python.org/pep-0621/
"""

from __future__ import annotations

import re
from typing import Dict, List, Literal, Optional, Union

from packaging.version import VERSION_PATTERN
from pydantic import BaseModel, Field, FilePath, ValidationError, model_validator

from .utils import to_hyphen


def dasherize(field: str):
    return field.replace("-", "_")


class Author(BaseModel):
    name: str
    email: str


class ContentTypeAndCharset(BaseModel, alias_generator=to_hyphen):
    content_type: Optional[Literal["text/plain", "text/x-rst", "text/markdown"]] = None
    charset: Optional[str] = None


class File(BaseModel):
    file: FilePath


class Text(BaseModel):
    text: str


class FileWithContentType(File, ContentTypeAndCharset):
    pass


class TextWithContentType(Text, ContentTypeAndCharset):
    pass


ReadMe = Union[FilePath, FileWithContentType, TextWithContentType]


class ProjectMetadata(BaseModel, alias_generator=to_hyphen):
    name: str = Field(pattern=r"^([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9])$")
    version: Optional[str] = Field(
        None, pattern=re.compile(VERSION_PATTERN, re.IGNORECASE | re.VERBOSE)
    )
    description: Optional[str] = None
    readme: Optional[ReadMe] = None
    requires_python: Optional[str] = None
    license: Optional[Union[FilePath, File, Text]] = None
    authors: List[Author] = []
    maintainers: List[Author] = []
    keywords: List[str] = []
    classifiers: List[str] = []
    urls: Dict[str, str] = {}
    scripts: Dict[str, str] = {}
    gui_scripts: Dict[str, str] = {}
    entry_points: Dict[str, str] = {}
    dependencies: List[str] = []
    optional_dependencies: Dict[str, List[str]] = {}
    dynamic: List[
        Literal[
            "name",
            "version",
            "description",
            "readme",
            "requires-python",
            "license",
            "authors",
            "maintainers",
            "keywords",
            "classifiers",
            "urls",
            "scripts",
            "gui-scripts",
            "entry-points",
            "dependencies",
            "optional-dependencies",
        ]
    ] = []

    @model_validator(mode="after")
    def validate_license(self):
        if self.version is None and "version" not in self.dynamic:
            raise ValidationError("Field version is required")
