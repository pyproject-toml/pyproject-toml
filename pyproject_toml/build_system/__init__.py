from typing import List, Optional

from pydantic import BaseModel, DirectoryPath, ValidationError, model_validator

from ..utils import to_hyphen


class BuildSystemMetadata(BaseModel, alias_generator=to_hyphen):
    requires: List[str]
    build_backend: Optional[str] = None
    backend_path: List[DirectoryPath] = []

    @model_validator(mode="after")
    def validate_backend_path(self):
        for path in self.backend_path:
            if path.is_absolute():
                raise ValidationError("backend-path must be relative")
            if ".." in path.parts:
                raise ValidationError("backend-path must not contain '..'")
