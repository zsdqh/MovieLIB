from typing import Type, TypeVar

from pydantic import BaseModel
from starlette.requests import Request

T = TypeVar("T", bound=BaseModel)


async def form_to_pydantic(request: Request, model: Type[T]) -> T:
    """Преобразование http формы в pydantic модель"""
    return model(**dict(await request.form()))
