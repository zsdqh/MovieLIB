from typing import Any

from pydantic import BaseModel


def pydantic_to_api(model: BaseModel) -> dict[str, Any]:
    """
    Преобразование базовой модели pydantic со snake_case нотацией
    в dict с camelCase нотацией и валидными ключами для стороннего API
    """
    res = {}
    for name, value in model:
        if value is None:
            continue
        if name in ["genres", "countries"]:
            name += ".name"
        if name == "rating":
            name += ".kp"

        camel_name = []

        # убираем нижние подчеркивания и делаем следующую букву большой
        # буквально превращаем snake_case в camelCase
        f = False
        for char in name:
            if char == "_":
                f = True
            else:
                camel_name.append(char if not f else char.upper())
                f = False
        res["".join(camel_name)] = value
    return res
