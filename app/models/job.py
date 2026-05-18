from datetime import datetime, timedelta
from typing import Optional

from django.db import models
from django.utils import timezone
from django.db.models import CharField, TextField, JSONField
from django.db.models.enums import TextChoices
from django.db.models.fields.related import ForeignKey

from app.models import User
from app.models.base_model import BaseModel


class Job(BaseModel):
    class ATTACHMENT_NAMES(TextChoices):
        RESULT_OBJECT = "result_object"

    class STATUSES(TextChoices):
        TODO = "TODO"
        IN_PROGRESS = "IN_PROGRESS"
        DONE = "DONE"
        FAILED = "FAILED"
        WAITING = "WAITING"
        STOP = "STOP"

    class DatabaseFields:
        uuid = "uuid"
        created_at = "created_at"
        updated_at = "updated_at"
        queue = "queue"
        status = "status"
        failed_reason = "failed_reason"
        payload = "payload"
        available_at = "available_at"
        started_at = "started_at"
        progress = "progress"
        retries = "retries"
        attachments = "attachments"
        user = "user"
        deleted_at = "deleted_at"

    class RESPONSE_FIELDS:
        queue = "queue"
        status = "status"
        failed_reason = "failed_reason"
        payload = "payload"
        available_at = "available_at"
        started_at = "started_at"
        progress = "progress"
        retries = "retries"
        attachments = "attachments"
        user = "user"
        scheduled_at = "scheduled_at"

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        db_table = "jobs"
        db_table_comment = "Jobs table"
        get_latest_by = "created_at"
        ordering = ["created_at"]

    queue = CharField(max_length=256, db_index=True, db_comment="Queue name")
    status = CharField(
        max_length=256,
        db_index=True,
        choices=STATUSES.choices,
        default=STATUSES.TODO,
        db_default=STATUSES.TODO,
        db_comment="Status of the job",
    )
    failed_reason = TextField(null=True, db_comment="Reason for the job failure")
    payload = JSONField(null=True, db_comment="Payload of the job")
    available_at = models.DateTimeField(
        null=True, db_index=True, db_comment="Available at timestamp"
    )
    started_at = models.DateTimeField(
        null=True, db_index=True, db_comment="Started at timestamp"
    )
    progress = models.FloatField(
        null=True, db_index=True, db_comment="Progress of the job"
    )
    retries = models.IntegerField(
        null=True, db_index=True, db_comment="Number of retries"
    )
    attachments = JSONField(null=True, db_comment="Attachments related to the job")
    user = ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name="jobs",
        db_column="user_id",
        db_comment="The job is running for this user",
    )

    def __str__(self):
        """
        Returns a string representation of the Job object.

        Returns:
            str: A string representation of the Job object in the format "Job {self.uuid}"
        """
        return f"Job {self.queue}-{self.status}-{self.uuid}"

    def set_available_at(self, date: datetime | None = None) -> None:
        """
        Sets the available_at attribute of the Job object to the provided date or the current date if no date is provided.

        Args:
            date (datetime | None): The date to set as available_at. If None, the current date is used.
        """
        self.available_at = (
            date.isoformat() if date is not None else timezone.now().isoformat()
        )

    def set_started_at(self, date: datetime | None = None) -> None:
        """
        Sets the started_at attribute of the Job object to the provided date or the current date if no date is provided.

        Args:
            date (datetime | None): The date to set as started_at. If None, the current date is used.
        """
        self.started_at = (
            date.isoformat() if date is not None else timezone.now().isoformat()
        )

    def is_available(self):
        """
        Checks if the Job object can be processed.

        Returns:
            bool: True if the Job object is available, False otherwise.
        """
        if self.status != self.STATUSES.TODO.value:
            return False
        if self.available_at is None:
            return True
        available_at = self.available_at
        return datetime.now(available_at.tzinfo) > available_at

    def success(self) -> None:
        """
        Marks the Job object as done and sets the failed_reason attribute.
        """
        self.status = Job.STATUSES.DONE.value
        self.save()

    def fail(self, message: str | None = None) -> None:
        """
        Marks the Job object as failed and sets the failed_reason attribute.

        Args:
            message (str | None): The reason for the job failure. If None, the failed_reason attribute is not updated.
        """
        self.status = Job.STATUSES.FAILED.value
        self.failed_reason = (
            message
            + " \n last message: "
            + (str(self.failed_reason) if self.failed_reason else "nothing")
        )
        self.save()

    def start(self):
        """
        Marks the Job object as started and sets the started_at attribute to the current date.
        """
        self.status = Job.STATUSES.IN_PROGRESS.value
        self.set_started_at()
        self.available_at = None
        self.save()

    def retry(
        self, delay_in_minutes: int, max_retries: int | None, message: str | None = None
    ) -> None:
        """
        Marks the Job object as ready to be retried after a specified delay.

        Args:
            delay_in_minutes (int): The delay in minutes before the job is retried.
            max_retries (int | None): The maximum number of retries allowed. If None, there is no limit.
            message (str | None): The reason for the job retry. If None, the failed_reason attribute is not updated.
        """
        retries = int(self.retries) + 1 if self.retries is not None else 1
        if max_retries is not None and retries > max_retries:
            self.fail(f"Max retries exceeded \n\n {message}")
            return
        self.retries = retries
        self.status = Job.STATUSES.TODO.value
        self.failed_reason = message
        import random

        margin = random.randint(-60, 60)
        self.set_available_at(
            timezone.now() + timedelta(seconds=60 * delay_in_minutes + margin)
        )
        self.save()

    def get_payload_field(self, field_name: str):
        """
        Returns the value of a specific field from the payload attribute of the Job object.

        Args:
            field_name (str): The name of the field to retrieve.

        Returns:
            Any: The value of the specified field from the payload attribute. If the field does not exist, returns None.
        """
        payload = self.payload
        if payload is None:
            return None
        return payload[field_name] if field_name in payload else None

    def set_payload_field(self, field_name: str, value):
        """
        Sets the value of a specific field in the payload attribute of the Job object.

        Args:
            field_name (str): The name of the field to update.
            value (Any): The new value for the specified field.
        """
        payload = self.payload
        if payload is None:
            payload = {}

        payload[field_name] = value
        self.payload = payload

    def is_stopped(self, job_uuid: Optional[str] = None) -> bool:
        """
        Checks if the Job object with the specified UUID is stopped.

        Args:
            job_uuid (str | None): The UUID of the Job object to check. If None, the UUID of the current Job object is used.

        Returns:
            bool: True if the Job object is stopped, False otherwise.
        """
        from app.modules.provider.data_provider import DataProvider

        job_uuid = job_uuid if job_uuid is not None else self.uuid
        if job_uuid is not None:
            job = DataProvider.job(uuid=job_uuid)
            return job is not None and job.status == Job.STATUSES.STOP.value
        return False

    def api_response(
        self,
        other_properties: dict | None = None,
        add_user_info: bool = False,
        **kwargs,
    ) -> dict:
        properties = {
            BaseModel.RESPONSE_FIELDS.type: self.__class__.__name__,
            self.RESPONSE_FIELDS.queue: self.queue,
            self.RESPONSE_FIELDS.status: self.status,
            self.RESPONSE_FIELDS.failed_reason: self.failed_reason,
            self.RESPONSE_FIELDS.payload: self.payload,
            self.RESPONSE_FIELDS.available_at: (
                self.available_at.isoformat() if self.available_at else None
            ),
            self.RESPONSE_FIELDS.started_at: (
                self.started_at.isoformat() if self.started_at else None
            ),
            self.RESPONSE_FIELDS.progress: self.progress,
            self.RESPONSE_FIELDS.retries: self.retries,
            self.RESPONSE_FIELDS.attachments: self.attachments,
            **(
                {self.RESPONSE_FIELDS.user: self.user.api_response(**kwargs)}
                if self.user and add_user_info
                else {
                    self.RESPONSE_FIELDS.user: (
                        str(self.user.uuid) if self.user else None
                    )
                }
            ),
            **(other_properties or {}),
        }
        return super().api_response(properties, **kwargs)

    @classmethod
    def api_response_schema(
        cls,
        other_properties: dict | None = None,
        add_user_info: bool = False,
        **kwargs,
    ) -> dict:
        from app.models.user import User

        properties = {
            **(other_properties or {}),
            BaseModel.RESPONSE_FIELDS.type: {
                "type": "string",
                "title": "Item Type",
                "description": "Item Type",
                "readonly": True,
                "required": True,
                "nullable": False,
                "example": cls.__name__,
            },
            cls.RESPONSE_FIELDS.queue: {
                "type": "string",
                "title": "Queue",
                "nullable": False,
                "readonly": False,
                "required": True,
            },
            cls.RESPONSE_FIELDS.status: {
                "type": "string",
                "title": "Status",
                "enum": cls.STATUSES.values,
                "readonly": False,
                "required": True,
                "nullable": False,
                "example": cls.STATUSES.TODO.value,
            },
            cls.RESPONSE_FIELDS.failed_reason: {
                "type": "string",
                "title": "Failed Reason",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Reason for the job failure",
            },
            cls.RESPONSE_FIELDS.payload: {
                "type": "object",
                "title": "Payload",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Payload of the job",
            },
            cls.RESPONSE_FIELDS.available_at: {
                "type": "string",
                "format": "date-time",
                "title": "Available At",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Available at timestamp",
            },
            cls.RESPONSE_FIELDS.started_at: {
                "type": "string",
                "format": "date-time",
                "title": "Started At",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Started at timestamp",
            },
            cls.RESPONSE_FIELDS.progress: {
                "type": "number",
                "title": "Progress",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Progress of the job",
            },
            cls.RESPONSE_FIELDS.retries: {
                "type": "integer",
                "title": "Retries",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Number of retries",
            },
            cls.RESPONSE_FIELDS.attachments: {
                "type": "object",
                "title": "Attachments",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Attachments of the job",
            },
            cls.RESPONSE_FIELDS.scheduled_at: {
                "type": "string",
                "format": "date-time",
                "title": "Scheduled At",
                "nullable": True,
                "readonly": False,
                "required": False,
                "description": "Scheduled send time (alias for available_at)",
            },
            **(
                {cls.RESPONSE_FIELDS.user: User.api_response_schema(**kwargs)}
                if add_user_info
                else {
                    cls.RESPONSE_FIELDS.user: {
                        "type": "string",
                        "format": "uuid",
                        "title": "User UUID",
                        "nullable": False,
                        "readonly": False,
                        "required": True,
                        "description": "User UUID",
                    }
                }
            )
        }
        return super().api_response_schema(properties, **kwargs)
