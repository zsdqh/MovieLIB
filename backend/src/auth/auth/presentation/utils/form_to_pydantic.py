import json
from typing import Type, TypeVar

from pydantic import BaseModel
from starlette.requests import Request

T = TypeVar("T", bound=BaseModel)


async def form_to_pydantic(request: Request, model: Type[T]) -> T:
    """Преобразование http формы в pydantic модель"""
    data = await request.form()
    if not data:
        # Если пришел json в body, а не форма
        # нужно для обратной совместимости и тестов
        data = json.loads(await request.body())
    return model(**dict(data))
