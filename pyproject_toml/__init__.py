from __future__ import annotations

from typing import List, Optional, Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
)

from .build_system import BuildSystemMetadata
from .project import ProjectMetadata
from .utils import to_hyphen


class ToolPyProjectToml(BaseModel):
    packages: List[str]


class Tool(BaseModel, alias_generator=to_hyphen, extra="allow"):
    pyproject_toml: Optional[ToolPyProjectToml] = None


class PyProjectToml(BaseSettings, alias_generator=to_hyphen, pyproject_toml_table_header=()):
    project: Optional[ProjectMetadata] = None
    build_system: Optional[BuildSystemMetadata] = None
    tool: Tool = Tool()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)

settings = PyProjectToml()
