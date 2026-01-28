from backend.src.files.domain.interfaces.s3_worker import IS3Worker


class FileUseCase:
    """Базовый вариант использования работы с файлами"""

    def __init__(self, s3_worker: IS3Worker):
        """Внедрение зависимости s3 совместимого хранилища"""
        self.storage = s3_worker
