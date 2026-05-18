from typing import TYPE_CHECKING


from django.db import models
from django.db.models.enums import TextChoices
from app.models.base_api_model import BaseApiModel
from app.models.base_model import BaseModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

if TYPE_CHECKING:
    from app.models.api_key import ApiKey


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        # Always store email in lowercase for consistency
        email = self.normalize_email(email)
        if isinstance(email, str):
            email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel, BaseApiModel):
    class DatabaseFields:
        uuid = "uuid"
        created_at = "created_at"
        updated_at = "updated_at"
        name = "name"
        status = "status"
        email = "email"
        last_login = "last_login"
        password = "password"
        profile_image = "profile_image"
        deleted_at = "deleted_at"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"
        db_table_comment = "Users table"
        get_latest_by = "created_at"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["name"], name="user_name_idx"),
            models.Index(fields=["email"], name="user_email_idx"),
        ]

    class STATUSES(TextChoices):
        ACTIVE = "ACTIVE"
        SUSPENDED = "SUSPENDED"
        DELETED = "DELETED"

    class RESPONSE_FIELDS:
        name = "name"
        email = "email"
        status = "status"
        profile_image = "profile_image"
        is_staff = "is_staff"
        is_superuser = "is_superuser"

    name = models.CharField(
        null=False, max_length=256, db_index=True, db_comment="Name of the user"
    )
    status = models.CharField(
        max_length=64,
        choices=STATUSES.choices,
        default=STATUSES.ACTIVE,
        db_index=True,
        db_comment="Status of this user EX: ACTIVE, SUSPENDED, DELETED",
        db_default=STATUSES.ACTIVE,
        null=False,
    )
    email = models.EmailField(null=False, db_comment="Email of the user", unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=128, null=True)
    profile_image = models.JSONField(null=True, db_comment="Profile image of the user")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        """
        Override save to ensure email is always stored in lowercase.

        This keeps authentication behavior consistent and avoids duplicate
        accounts that differ only by email case.
        """
        if isinstance(self.email, str):
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_profile_image_url(self):
        attachment = self.get_attachment(
            attachments_parameter_name=self.DatabaseFields.profile_image,
        )
        if attachment is None:
            return None
        from app.config.app import AppConfig

        return f"{AppConfig.BASE_URL}{attachment.url}"

    def add_profile_image(
        self, image_url: str, file_name: str, file_type: str | None = "jpg"
    ):
        """
        This function adds a profile image to the user's record by downloading the image from the given URL and
        attaching it to the user's record.
        If the user already has a profile image, the function does not add a duplicate.

        Parameters:
        - image_url (str): The URL from which to download the profile image.
        - file_name (str): The name to be assigned to the profile image file.
        - file_type (str | None): The type of the profile image file. Default is 'jpg'.

        Returns:
        - None
        """
        current_image = self.get_attachment(
            file_name=file_name,
            attachments_parameter_name=self.DatabaseFields.profile_image,
        )
        if current_image is None:
            import requests

            with requests.get(image_url) as f:
                file_content = f.content
                self.add_attachment_file(
                    file_name,
                    file_content,
                    User.DatabaseFields.profile_image,
                    file_type,
                )

    def api_response(
        self,
        other_properties: dict | None = None,
        **kwargs,
    ) -> dict:
        properties = {
            BaseModel.RESPONSE_FIELDS.type: self.__class__.__name__,
            self.RESPONSE_FIELDS.name: self.name,
            self.RESPONSE_FIELDS.email: self.email,
            self.RESPONSE_FIELDS.status: self.status,
            self.RESPONSE_FIELDS.profile_image: self.get_profile_image_url(),
            self.RESPONSE_FIELDS.is_staff: self.is_staff,
            self.RESPONSE_FIELDS.is_superuser: self.is_superuser,
            **(other_properties or {}),
        }
        return super().api_response(properties, **kwargs)

    @classmethod
    def api_response_schema(
        cls,
        other_properties: dict | None = None,
        **kwargs,
    ) -> dict:
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
            cls.RESPONSE_FIELDS.name: {
                "type": "string",
                "title": "Name",
                "description": "Name of the user",
                "readonly": False,
                "required": True,
                "nullable": False,
                "example": "John Doe",
            },
            cls.RESPONSE_FIELDS.email: {
                "type": "string",
                "title": "Email",
                "description": "Email of the user",
                "readonly": False,
                "required": True,
                "nullable": False,
                "example": "john@example.com",
            },
            cls.RESPONSE_FIELDS.status: {
                "type": "string",
                "title": "Status",
                "description": "Status of this user",
                "enum": cls.STATUSES.values,
                "readonly": False,
                "required": True,
                "nullable": False,
                "example": cls.STATUSES.ACTIVE.value,
            },
            cls.RESPONSE_FIELDS.profile_image: {
                "type": "string",
                "title": "Profile Image",
                "description": "Profile Image URL",
                "example": "https://example.com/profile.jpg",
                "nullable": True,
                "readonly": False,
                "required": False,
            },
        }
        return super().api_response_schema(properties, **kwargs)

    def can_access_user(self, target_user: "User") -> bool:
        """
        Check if this user has access to view/manage the target user.

        Access rules:
        - Admins/staff can access everyone.
        - Users can always access themselves.

        Args:
            target_user: The user to check access for.

        Returns:
            bool: True if this user can access the target user.
        """
        from app.modules.provider.data_provider import DataProvider

        # Can always access self
        if self.uuid == target_user.uuid:
            return True
        if self.is_staff or self.is_superuser:
            return True

        return False
