import uuid
from io import StringIO, BytesIO
from typing import List, Optional, TYPE_CHECKING

from django.core.files.storage import default_storage
from django.db import models
from pydantic import BaseModel as PydanticModel
from django.db.models.functions import Now
from django.contrib.postgres.functions import RandomUUID

from app.models.base_api_model import BaseApiModel

if TYPE_CHECKING:
    from app.models.job import Job


class Attachment(PydanticModel):
    filename: str
    url: str
    storage_path: str

    @property
    def full_url(self) -> str:
        from app.utils.url_util import UrlUtil

        return UrlUtil.get_route(self.url)


class Attachments(PydanticModel):
    items: List[Attachment] = []


class SoftDeleteManager(models.Manager):
    """
    A custom manager for handling soft deletion in Django models.

    This manager provides methods to retrieve objects based on their deletion status.

    Example usage:
        User.objects.all(): Returns only active (non-deleted) users.
        User.objects.all_with_deleted(): Returns all users, including soft-deleted ones.
        User.objects.only_deleted(): Returns only soft-deleted users.
    """

    def get_queryset(self):
        """
        Override the default get_queryset method to exclude soft-deleted items.

        Returns:
        QuerySet: A QuerySet containing only non-deleted items.
        """
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        """
        Return a QuerySet containing all records, including soft-deleted ones.

        Returns:
        QuerySet: A QuerySet containing all records.
        """
        return super().get_queryset()

    def only_deleted(self):
        """
        Return a QuerySet containing only soft-deleted records.

        Returns:
        QuerySet: A QuerySet containing only soft-deleted items.
        """
        return super().get_queryset().filter(deleted_at__isnull=False)


class BaseModel(models.Model, BaseApiModel):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_comment="UUID for each record",
        db_default=RandomUUID(),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        db_comment="Creation timestamp",
        db_default=Now(),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        db_comment="Last update timestamp",
        db_default=Now(),
    )
    deleted_at = models.DateTimeField(
        auto_now=False,
        db_index=True,
        db_comment="Soft deletion timestamp",
        db_default=None,
        null=True,
    )

    # for pycharm compatibility
    objects = models.Manager()

    # for pycharm compatibility
    objects = SoftDeleteManager()

    def delete(self, *args, **kwargs):
        # Soft-delete: set deleted_at instead of actually deleting
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        # Restore the soft-deleted record
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        # Hard delete: delete the record permanently
        super().delete()

    class Meta:
        abstract = True

    def add_attachment_file(
        self,
        file_name: str,
        file_content: str | bytes,
        attachments_parameter_name: str = "attachments",
        file_type: str = "json",
        delete_file_from_storage_after_in_minutes: int | None = None,
        overwrite_file: bool = True,
        save_in_db: bool = True,
    ) -> tuple[Attachments, Optional["Job"]]:
        """
        Adds a new attachment file to the current model instance.

        Parameters:
        - file_name (str): The name of the file to be attached.
        - content (str): The content of the file to be attached.
        - attachments_parameter_name (str): The name of the attribute in the model instance that holds the attachments. Default is 'attachments'.
        - file_type (str): The type of the file. Default is 'json'.
        - delete_file_from_storage_after_in_minutes (int | None): The number of minutes after which the file should be deleted from storage. If None, the file will not be deleted. Default is None.
        - overwrite_file (bool): Whether to overwrite an existing file with the same name. Default is True.

        Returns:
        - Attachments: The updated list of attachments after adding the new file.
        """
        # Get the existing attachments
        attachments = getattr(self, attachments_parameter_name)
        if not isinstance(attachments, dict):
            attachments = {}
        attachments = Attachments.model_validate(attachments)

        # Overwrite the existing file if necessary
        if overwrite_file and attachments is not None:
            new_attachments = Attachments()
            for attachment in attachments.items:
                if attachment.filename == file_name:
                    if default_storage.exists(attachment.storage_path):
                        default_storage.delete(attachment.storage_path)
                else:
                    new_attachments.items.append(attachment)
            attachments = new_attachments

        # Generate a unique record ID
        record_id = self.uuid
        if record_id is None or record_id == "":
            from app.utils.string_util import StringUtil

            record_id = StringUtil.random_string()

        # Store the file using Django's file storage
        if isinstance(file_content, str):
            content = StringIO(file_content)
        elif isinstance(file_content, bytes):
            content = BytesIO(file_content)
        else:
            raise ValueError("Invalid file_content type. Expected str or bytes.")

        path = f"{self.__class__.__name__}/{record_id}_{file_name}.{file_type}"
        file_project_path = default_storage.save(path, content)
        delete_job = None
        if (
            delete_file_from_storage_after_in_minutes
            and delete_file_from_storage_after_in_minutes > 0
        ):
            # Schedule the file deletion using Django's task scheduler
            from app.tasks.delete_temporary_file import DeleteTemporaryFileJob

            delete_job = DeleteTemporaryFileJob.create_new_job(
                path=path,
                delay_in_seconds=delete_file_from_storage_after_in_minutes * 60,
            )
        url = default_storage.url(file_project_path)
        new_attachment = Attachment(filename=file_name, url=url, storage_path=path)

        # Add the new attachment to the existing attachments
        attachments.items.append(new_attachment)
        # Update the attachment field in the database
        setattr(self, attachments_parameter_name, attachments.model_dump())
        if save_in_db:
            self.save()

        return attachments, delete_job

    def get_attachment(
        self,
        file_name: str | None = None,
        attachments_parameter_name: str = "attachments",
    ) -> Optional[Attachment]:
        """
        Retrieves an attachment file based on its filename if provided else it would return the first attachment

        Parameters:
        - file_name (str | None ): The name of the file to retrieve the URL for.
        - attachments (dict | None): The list of attachments to search for the file. If None, the method will look for
         the attachments in the current model instance.

        Returns:
        - Attachment: The attachment file if found, otherwise None.
        """
        attachments = getattr(self, attachments_parameter_name)
        if not isinstance(attachments, dict):
            attachments = {}
        attachments = Attachments.model_validate(attachments)
        if attachments is not None:
            attachments = Attachments.model_validate(attachments)
            for attachment in attachments.items:
                if file_name is not None:
                    if attachment.filename == file_name:
                        return attachment
                else:
                    return attachment
        return None

    def api_response(self, other_properties: dict | None = None, **kwargs) -> dict:
        """
        Generates a dictionary representing the API response of the current model instance.

        Args:
        - other_properties (dict | None): Additional properties to include in the response. Default is None.
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: A dictionary representing the API response of the current model instance.
        """
        from datetime import datetime, timezone

        # Handle created_at - it might be a DatabaseDefault if object is unsaved
        if hasattr(self.created_at, "isoformat"):
            created_at_str = self.created_at.isoformat()
        else:
            # Fallback to current datetime if created_at is not a datetime object
            created_at_str = datetime.now(timezone.utc).isoformat()

        return {
            BaseApiModel.RESPONSE_FIELDS.type: self.__class__.__name__,
            BaseApiModel.RESPONSE_FIELDS.key: str(self.uuid),
            BaseApiModel.RESPONSE_FIELDS.created_at: created_at_str,
            **(other_properties or {}),
        }

    @classmethod
    def api_response_schema(
        cls, other_properties: dict | None = None, **kwargs
    ) -> dict:
        """
        Generates a JSON schema for the API response of the current model instance.

        Args:
        - other_properties (dict | None): Additional properties to include in the schema. Default is None.
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: A JSON schema representing the API response of the current model instance.
        """
        return {
            "type": "object",
            "properties": {
                **(other_properties or {}),
                BaseApiModel.RESPONSE_FIELDS.type: {
                    "type": "string",
                    "title": "Item Type",
                    "description": "Item Type",
                    "readonly": True,
                    "required": True,
                    "nullable": False,
                    "example": cls.__class__.__name__,
                },
                BaseApiModel.RESPONSE_FIELDS.key: {
                    "type": "string",
                    "title": "Key",
                    "description": "Unique identifier for this item",
                    "readonly": True,
                    "required": True,
                    "nullable": False,
                    "format": "uuid",
                    "example": "9c2e8220-20d8-4835-ba9b-3eef7fcac6ff",
                },
                BaseApiModel.RESPONSE_FIELDS.created_at: {
                    "type": "string",
                    "title": "Creation Date",
                    "description": "Creation Date of this item",
                    "readonly": True,
                    "required": True,
                    "nullable": False,
                    "format": "date-time",
                    "example": "2024-10-20T12:52:32.013853",
                },
            },
            "required": [BaseApiModel.RESPONSE_FIELDS.type],
        }
