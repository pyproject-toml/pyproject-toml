"""A PEP 517 interface port from setuptools
This is not a formal definition! Just a "taste" of the module.
"""

from setuptools.build_meta import (
    SetupRequirementsError,
    build_editable,
    build_sdist,
    build_wheel,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

__all__ = [
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_editable",
    "prepare_metadata_for_build_wheel",
    "build_wheel",
    "build_sdist",
    "build_editable",
    "SetupRequirementsError",
]
