from backend.src.core.domain.exceptions import BadRequestException


class InvalidFileException(BadRequestException):
    """Файл имеет неправильный формат или был поврежден"""

    detail = "Invalid file format"
