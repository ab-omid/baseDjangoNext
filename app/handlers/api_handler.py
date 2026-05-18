import json
from datetime import datetime
from typing import Any, TYPE_CHECKING

import requests
from django.db import IntegrityError

from app.actions.action import Action
from app.handlers.handler import Handler
from app.models.api_key import ApiKey
from app.models.job import Job
from app.models.user import User
from app.modules.provider.data_provider import BasicList, DataProvider

if TYPE_CHECKING:
    from datetime import date, datetime


class ApiHandler(Handler):
    @classmethod
    def users(
        cls,
        admin_user: User,
        search: str = None,
        page_token: str = None,
        max_results: int = 10,
    ) -> Action:
        """
        Get list of users based on access control.

        Args:
            admin_user (User): The user requesting the list.
            search (str, optional): Search term for filtering users.
            page_token (str, optional): Pagination token.
            max_results (int, optional): Maximum number of users to return. Defaults to 10.

        Returns:
            Action: Action with list of users or error.
        """
        if not admin_user or admin_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        users = DataProvider.users_accessible_for_user(
            admin_user,
            search=search,
            max_results=max_results,
            page_token=page_token,
        )

        return cls.action(
            Action.prepare_api_output(
                users.items,
                users.next_page_token,
                users.previous_page_token,
                users.total_results,
                check_connection_status=True,
            )
        )
        
    

    @classmethod
    def user_detail(
        cls, current_user: User, target_user: str
    ) -> Action:
        """
        Get user details by UUID.

        Args:
            admin_user (User): The user requesting the details.
            user_uuid (str): UUID of the user to get details for.

        Returns:
            Action: Action with user details or error.
        """
        if not current_user or current_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        # Get user by UUID
        user = DataProvider.user(uuid=target_user)

        if not user:
            return cls.not_found(["User not found"])

        # Check access using can_access_user method
        if not current_user.can_access_user(user):
            return cls.forbidden(["Access denied: You cannot view this user"])

        return cls.action(user.api_response())

    @classmethod
    def create_user(
        cls,
        current_user: User | None = None,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        status: str | None = None,
        is_staff: bool | None = None,
        is_superuser: bool | None = None,
    ) -> Action:
        """Create a new user (admin/staff only)."""
        if not current_user or current_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        if not (current_user.is_staff or current_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can create users"])

        if not name:
            return cls.bad_request(["Name is required"])
        if not email:
            return cls.bad_request(["Email is required"])
        if not password:
            return cls.bad_request(["Password is required"])

        existing_user = DataProvider.user(email=email)
        if existing_user:
            return cls.bad_request(["Email is already taken"])

        if status is not None and status not in User.STATUSES.values:
            return cls.bad_request(
                [f"Invalid status. Valid statuses: {', '.join(User.STATUSES.values)}"]
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            status=status or User.STATUSES.ACTIVE,
            is_staff=bool(is_staff) if is_staff is not None else False,
            is_superuser=bool(is_superuser) if is_superuser is not None else False,
        )
        return cls.action(user.api_response())

    @classmethod
    def update_user(
        cls,
        current_user: User | None = None,
        target_user_uuid: str | None = None,
        name: str | None = None,
        email: str | None = None,
        status: str | None = None,
        is_staff: bool | None = None,
        is_superuser: bool | None = None,
    ) -> Action:
        """
        Update user by UUID.

        Args:
            admin_user (User): The admin user performing the update.
            user_uuid (str): UUID of the user to update.
            data (dict): Update data.

        Returns:
            Action: Action with updated user or error.
        """
        if not current_user or current_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        # Check if user is admin or staff
        if not (current_user.is_staff or current_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can update users"])

        # Get user by UUID
        if not target_user_uuid:
            return cls.bad_request(["User UUID is required"])

        user = DataProvider.user(uuid=target_user_uuid)

        if not user:
            return cls.not_found(["User not found"])

        # Update user fields
        if name is not None:
            user.name = name
        if email is not None:
            existing_user = DataProvider.user(email=email)
            if existing_user and existing_user.uuid != user.uuid:
                return cls.bad_request(["Email is already taken"])
            user.email = email
        if status is not None:
            if status not in User.STATUSES.values:
                return cls.bad_request(
                    [f"Invalid status. Valid statuses: {', '.join(User.STATUSES.values)}"]
                )
            user.status = status
        if is_staff is not None:
            user.is_staff = is_staff
        if is_superuser is not None:
            user.is_superuser = is_superuser

        user.save()

        return cls.action(user.api_response())

    @classmethod
    def delete_user(cls, current_user: User, target_user: str) -> Action:
        """
        Delete user by UUID.

        Args:
            admin_user (User): The admin user performing the deletion.
            user_uuid (str): UUID of the user to delete.

        Returns:
            Action: Action with success message or error.
        """
        if not current_user or current_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        # Get user by UUID
        user = DataProvider.user(uuid=target_user)

        if not user:
            return cls.not_found(["User not found"])

        # Check if user has access to delete target user
        if not current_user.can_access_user(user):
            return cls.forbidden(["Access denied: You cannot delete this user"])

        # Don't allow deleting yourself
        if user.uuid == current_user.uuid:
            return cls.bad_request(["Cannot delete yourself"])

        # Soft delete by setting status to DELETED
        user.status = User.STATUSES.DELETED
        user.deleted_at = datetime.now()
        user.save()

        return cls.action({"message": "User deleted successfully"})

    @classmethod
    def user_profile(
        cls, user: User | None = None
    ) -> Action:
        """
        Get current user profile.

        Args:
            user (User | None): The authenticated user.

        Returns:
            Action: Action with the user profile or error.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        user_dict = user.api_response()
        return cls.action(user_dict)

    @classmethod
    def update_user_profile(
        cls,
        user: User | None = None,
        name: str = None,
        email: str = None,
        password: str = None,
    ) -> Action:
        """
        Update current user profile.

        Args:
            user (User | None): The authenticated user.
            name (str): New name.
            email (str): New email.
            password (str): New password.

        Returns:
            Action: Action with the updated user profile or error.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        # Update fields if provided
        if name is not None:
            user.name = name

        if email is not None:
            # Check if email is already taken by another user
            from app.modules.provider.data_provider import DataProvider

            existing_user = DataProvider.user(email=email)
            if existing_user and existing_user.uuid != user.uuid:
                return cls.bad_request(["Email is already taken"])
            user.email = email

        if password is not None:
            user.set_password(password)

        # Save the user if any field was updated
        if any(param is not None for param in [name, email, password]):
            user.save()

        user_dict = user.api_response()
        return cls.action(user_dict)

    @classmethod
    def upload_user_profile_image(
        cls, user: User | None = None, profile_image=None
    ) -> Action:
        """
        Upload profile image for current user.

        Args:
            user (User | None): The authenticated user.
            profile_image: The uploaded file.

        Returns:
            Action: Action with the updated user profile or error.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        if not profile_image:
            return cls.bad_request(["Profile image file is required"])

        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if profile_image.content_type not in allowed_types:
            return cls.bad_request(
                ["Invalid file type. Only JPEG, PNG, and GIF are allowed"]
            )

        # Validate file size (max 5MB)
        if profile_image.size > 5 * 1024 * 1024:
            return cls.bad_request(["File size too large. Maximum size is 5MB"])

        try:
            # Add the profile image to the user
            file_name = f"user_profile_image_{user.uuid}"
            file_type = (
                profile_image.name.split(".")[-1]
                if "." in profile_image.name
                else "jpg"
            )

            user.add_attachment_file(
                file_name=file_name,
                file_content=profile_image.read(),
                attachments_parameter_name=User.DatabaseFields.profile_image,
                file_type=file_type,
            )

            user_dict = user.api_response()
            return cls.action(user_dict)

        except Exception as e:
            return cls.bad_request([f"Failed to upload profile image: {str(e)}"])

    @classmethod
    def update_job(
        cls,
        user: User | None = None,
        job_uuid: str | None = None,
        status: str | None = None,
        available_at=None,
    ) -> Action:
        """
        Update a job (status, available_at).

        Args:
            user: The authenticated user.
            job_uuid: Job UUID.
            status: Job status.
            available_at: Start datetime (ISO format string).

        Returns:
            Action: Action with updated job or error.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        if not job_uuid:
            return cls.bad_request(["Job UUID is required"])

        job = DataProvider.job(uuid=job_uuid)
        if not job:
            return cls.not_found(["Job not found"])

        if job.user:
            if not user.can_access_user(job.user):
                return cls.forbidden(
                    [
                        "Access denied: You can only update jobs for users you have access to"
                    ]
                )

        # Update fields
        if status is not None:
            from app.models.job import Job

            if status in Job.STATUSES.values:
                job.status = status

        # available_at is already parsed in the controller
        if available_at is not None:
            job.available_at = available_at

        job.save()

        return cls.action(job.api_response(add_user_info=False))

    # ── API Key Management ────────────────────────────────────────────────

    @classmethod
    def get_api_key(cls, user: "User | None" = None) -> "Action":
        """
        Get the current user's API key metadata (prefix, scopes, last_used_at).
        Never returns the raw key.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        api_key = DataProvider.api_key(user=user)
        if not api_key:
            return cls.action(None)

        return cls.action(api_key.api_response())

    @classmethod
    def generate_api_key(
        cls,
        user: "User | None" = None,
        name: str | None = None,
        scopes: list[str] | None = None,
    ) -> "Action":
        """
        Generate a new API key for the authenticated user, revoking any existing one.
        Returns the raw key exactly once.
        """
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        from app.models.api_key import ApiKey

        if scopes:
            invalid = [s for s in scopes if s not in ApiKey.SCOPES.values]
            if invalid:
                return cls.bad_request(
                    [
                        f"Invalid scopes: {', '.join(invalid)}. Valid scopes: {', '.join(ApiKey.SCOPES.values)}"
                    ]
                )

        api_key, raw_key = ApiKey.generate(
            user=user,
            name=name or "Default",
            scopes=scopes,
        )

        response = api_key.api_response()
        response["raw_key"] = raw_key
        return cls.action(response)

    @classmethod
    def generate_api_key_for_user(
        cls,
        current_user: "User | None" = None,
        target_user_uuid: str | None = None,
        name: str | None = None,
        scopes: list[str] | None = None,
    ) -> "Action":
        """
        Generate a new API key for a target user (admin/staff only).
        Returns the raw key exactly once.
        """
        if not current_user or current_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])
        if not (current_user.is_staff or current_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can manage user API keys"])
        if not target_user_uuid:
            return cls.bad_request(["Target user UUID is required"])

        target_user = DataProvider.user(uuid=target_user_uuid)
        if not target_user:
            return cls.not_found(["User not found"])

        if scopes:
            invalid = [s for s in scopes if s not in ApiKey.SCOPES.values]
            if invalid:
                return cls.bad_request(
                    [
                        f"Invalid scopes: {', '.join(invalid)}. Valid scopes: {', '.join(ApiKey.SCOPES.values)}"
                    ]
                )

        api_key, raw_key = ApiKey.generate(
            user=target_user,
            name=name or "Default",
            scopes=scopes,
        )
        response = api_key.api_response()
        response["raw_key"] = raw_key
        return cls.action(response)

    @classmethod
    def revoke_api_key(cls, user: "User | None" = None) -> "Action":
        """Revoke (soft-delete) the current user's API key."""
        if not user or user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])

        api_key = DataProvider.api_key(user=user)
        if not api_key:
            return cls.not_found(["No API key found"])

        api_key.delete()
        return cls.action({"message": "API key revoked successfully"})
