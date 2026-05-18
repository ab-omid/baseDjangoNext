import hashlib
import secrets

from django.db import models
from django.db.models.enums import TextChoices

from app.models.base_model import BaseModel
from app.models.base_api_model import BaseApiModel


class ApiKey(BaseModel, BaseApiModel):
    """Per-user API key for programmatic access with scope-based permissions."""

    API_KEY_PREFIX = "pdnr_"
    API_KEY_BYTE_LENGTH = 32

    class DatabaseFields:
        uuid = "uuid"
        created_at = "created_at"
        updated_at = "updated_at"
        deleted_at = "deleted_at"
        user = "user"
        prefix = "prefix"
        hashed_key = "hashed_key"
        name = "name"
        scopes = "scopes"
        last_used_at = "last_used_at"

    class SCOPES(TextChoices):
        READ = "READ"
        WRITE = "WRITE"

    ALL_SCOPES = [SCOPES.READ, SCOPES.WRITE]

    class RESPONSE_FIELDS:
        name = "name"
        prefix = "prefix"
        scopes = "scopes"
        last_used_at = "last_used_at"

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="api_keys",
        db_index=True,
        db_comment="Owner of this API key",
    )
    prefix = models.CharField(
        max_length=16,
        db_index=True,
        db_comment="Unhashed prefix for identification (e.g. ubk_a1b2c3d4)",
    )
    hashed_key = models.CharField(
        max_length=128,
        unique=True,
        db_comment="SHA-256 hash of the full API key",
    )
    name = models.CharField(
        max_length=128,
        default="Default",
        db_comment="Human-readable label for this key",
    )
    scopes = models.JSONField(
        default=list,
        db_comment="List of permission scopes (READ, WRITE)",
    )
    last_used_at = models.DateTimeField(
        null=True,
        db_comment="Last time this key was used to authenticate",
    )

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        db_table = "api_keys"
        db_table_comment = "User API keys for programmatic access"
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        indexes = [
            models.Index(fields=["prefix"], name="apikey_prefix_idx"),
            models.Index(fields=["hashed_key"], name="apikey_hashed_key_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    def has_scope(self, scope: str) -> bool:
        return scope in (self.scopes or [])

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @classmethod
    def generate(cls, user, name: str = "Default", scopes: list[str] | None = None) -> tuple["ApiKey", str]:
        """
        Create a new API key for the given user.
        Revokes (soft-deletes) any existing key for this user (one-key-per-user policy).

        Returns:
            Tuple of (ApiKey instance, raw_key).
            raw_key is only available at creation time -- it cannot be retrieved later.
        """
        if scopes is None:
            scopes = cls.ALL_SCOPES

        cls.objects.filter(user=user).delete()

        raw_key = cls.API_KEY_PREFIX + secrets.token_urlsafe(cls.API_KEY_BYTE_LENGTH)
        instance = cls.objects.create(
            user=user,
            prefix=raw_key[:12],
            hashed_key=cls.hash_key(raw_key),
            name=name,
            scopes=scopes,
        )
        return instance, raw_key

    def api_response(self, other_properties: dict | None = None, **kwargs) -> dict:
        properties = {
            self.RESPONSE_FIELDS.name: self.name,
            self.RESPONSE_FIELDS.prefix: self.prefix,
            self.RESPONSE_FIELDS.scopes: self.scopes or [],
            self.RESPONSE_FIELDS.last_used_at: (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
        }
        if other_properties:
            properties.update(other_properties)
        return super().api_response(properties, **kwargs)

    @classmethod
    def api_response_schema(cls, other_properties: dict | None = None, **kwargs) -> dict:
        properties = {
            **(other_properties or {}),
            cls.RESPONSE_FIELDS.name: {
                "type": "string",
                "title": "Name",
                "description": "Human-readable label for this key",
                "example": "Default",
            },
            cls.RESPONSE_FIELDS.prefix: {
                "type": "string",
                "title": "Prefix",
                "description": "Unhashed prefix for identification",
                "example": "ubk_a1b2c3d4",
            },
            cls.RESPONSE_FIELDS.scopes: {
                "type": "array",
                "items": {"type": "string", "enum": cls.SCOPES.values},
                "title": "Scopes",
                "description": "Permission scopes",
            },
            cls.RESPONSE_FIELDS.last_used_at: {
                "type": "string",
                "format": "date-time",
                "title": "Last Used At",
                "nullable": True,
            },
        }
        return super().api_response_schema(properties, **kwargs)
