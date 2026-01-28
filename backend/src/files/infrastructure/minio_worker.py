import json
from contextlib import AbstractAsyncContextManager
from io import BytesIO
from tempfile import SpooledTemporaryFile
from typing import IO, Any

import aioboto3
from types_aiobotocore_s3.client import S3Client

from backend.src.core.config import MinioSettings
from backend.src.files.domain.exceptions import InvalidFileException
from backend.src.files.domain.interfaces.s3_worker import IS3Worker


class MinioWorker(IS3Worker):
    """MinIO реализация интерфейса для работы с s3 совместимым хранилищем"""

    def __init__(self, settings: MinioSettings) -> None:
        """Создание сессии aioboto3, совместимой с minio"""
        self.session = aioboto3.Session(
            region_name="us-east-1",
            aws_access_key_id=settings.user,
            aws_secret_access_key=settings.password,
        )
        self.settings = settings

    def _to_iobytes(self, data: Any) -> IO[Any]:
        """Преобразование данных для записи в подходящий формат"""
        try:
            if isinstance(data, (IO, SpooledTemporaryFile)):
                return data
            if isinstance(data, bytes):
                return BytesIO(data)
            return BytesIO(data.encode("utf-8"))
        except (ValueError, IOError) as e:
            raise InvalidFileException() from e

    def _get_client(self) -> AbstractAsyncContextManager[S3Client]:
        """Создание клиента для взаимодействия с minio"""
        return self.session.client("s3", endpoint_url=self.settings.url)

    def _get_bucket(self, is_avatar: bool) -> str:
        """Получение названия нужного бакета"""
        if is_avatar:
            return self.settings.avatar_bucket_name
        return self.settings.movie_bucket_name

    async def store_file(
        self, filename: str, file_data: Any, is_avatar: bool = False
    ) -> None:
        bucket = self._get_bucket(is_avatar)
        async with self._get_client() as client:
            await client.upload_fileobj(
                self._to_iobytes(file_data),
                bucket,
                filename,
            )

    async def delete_file(self, filename: str, is_avatar: bool = False) -> None:
        async with self._get_client() as client:
            await client.delete_object(Bucket=self._get_bucket(is_avatar), Key=filename)

    def get_link(self, filename: str, is_avatar: bool = False) -> str:
        """Ссылка на публичный объект(постоянная)"""
        return f"{self.settings.external_url}/{self._get_bucket(is_avatar)}/{filename}"

    def get_name_from_link(self, url: str, is_avatar: bool = False) -> str:
        return url.replace(
            f"{self.settings.external_url}/{self._get_bucket(is_avatar)}/", "", 1
        )

    async def set_bucket_policy(self) -> None:
        """Настройка политик бакетов"""
        async with self._get_client() as client:
            for bucket in [
                self.settings.avatar_bucket_name,
                self.settings.movie_bucket_name,
            ]:
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": ["s3:GetObject"],
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Resource": [f"arn:aws:s3:::{bucket}/*"],
                            "Sid": "",
                        }
                    ],
                }
                await client.put_bucket_policy(
                    Bucket=bucket,
                    Policy=json.dumps(policy),
                )
