import hashlib
from pydantic import BaseModel, PlainValidator, computed_field
from enum import Enum
from typing import Annotated


def _validate_md5(value: str) -> str:
    if len(value) != 32:
        raise ValueError('Invalid MD5 hash length. Must be exactly 32 characters.')
    return value


MD5Hash = Annotated[str, PlainValidator(_validate_md5)]

class TaskRequest(BaseModel):
    hashes: list[MD5Hash]


class Task(BaseModel):
    hashes: list[str]

    @computed_field
    @property
    def id(self) -> str:
        task_data = ''.join(self.hashes)
        return hashlib.md5(task_data.encode()).hexdigest()


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusEnum(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    NOT_FOUND = "not_found"
