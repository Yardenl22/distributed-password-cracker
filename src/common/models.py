from pydantic import BaseModel, PlainValidator
from typing import Annotated


def validate_md5(value: str) -> str:
    if len(value) != 32:
        raise ValueError("Invalid MD5 hash length. Must be exactly 32 characters.")
    return value


MD5Hash = Annotated[str, PlainValidator(validate_md5)]


class TaskCreate(BaseModel):
    hashes: list[MD5Hash]


class TaskStatusResponse(BaseModel):
    task_id: int
    status: str
