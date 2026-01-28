from backend.src.files.application.base import FileUseCase
from backend.src.files.domain.interfaces.name_generator import INameGenerator
from backend.src.files.domain.interfaces.s3_worker import IS3Worker


class UploadFileUseCase(FileUseCase):
    """Помещение файла в приватное хранилище"""

    def __init__(self, s3_worker: IS3Worker, name_generator: INameGenerator):
        self.name_generator = name_generator
        super().__init__(s3_worker)
