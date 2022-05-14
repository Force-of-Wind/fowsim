from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(ManifestFilesMixin, S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION

    def get_valid_name(self, name: str) -> str:
        return name

class LocalMediaStorage(FileSystemStorage):
    def get_valid_name(self, name: str) -> str:
        return name
