from datetime import date, datetime
from typing import Literal, Optional, List, Any
from typing import TYPE_CHECKING

from django.db.models import Manager

import asyncio
from asgiref.sync import sync_to_async
from functools import wraps

from app.models.base_api_model import BaseApiModel


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import Job


class BasicList(BaseApiModel):
    class RESPONSE_FIELDS:
        total_results = "total_results"

    def __init__(
        self,
        items: Optional[List[Any]] = None,
        next_page_token: Optional[Any] = None,
        number_of_items: Optional[int] = None,
        total_results: Optional[int] = None,
        previous_page_token: Optional[Any] = None,
        manager: Optional[Manager] = None,
    ):
        self.items = items
        self.next_page_token = next_page_token
        self.number_of_items = (
            number_of_items
            if number_of_items is not None
            else len(items) if items else 0
        )
        self.total_results = total_results
        self.previous_page_token = previous_page_token
        self.manager = manager if manager else None

    def api_response(self, **kwargs) -> dict:
        return {
            BaseApiModel.RESPONSE_FIELDS.type: self.__class__.__name__,
            BaseApiModel.RESPONSE_FIELDS.items: [
                item.api_response(**kwargs)
                for item in self.items
                if isinstance(item, BaseApiModel)
            ],
            self.RESPONSE_FIELDS.total_results: self.total_results,
        }


class Pager:
    """
    A class used to paginate query results from a Django Manager.

    Attributes:
    - manager: The Django Manager object to paginate.
    - max_results: The maximum number of results to return per page.
    - order_by: The field to order the results by.
    - page_token: The token for pagination.
    - just_counter: A flag indicating whether to just count the total results.
    - count_total_results: A flag indicating whether to count the total results.
    """

    def __init__(
        self,
        manager: Manager,
        max_results: Optional[int] = None,
        order_by: str = "uuid",
        order: Literal["asc", "desc"] = "asc",
        page_token: Optional[str] = None,
        just_counter: bool = False,
        count_total_results: bool = False,
    ):
        """
        Initializes a new instance of the Pager class.

        Parameters:
        - manager: The Django Manager object to paginate.
        - max_results: The maximum number of results to return per page.
        - order_by: The field to order the results by.
        - page_token: The token for pagination.
        - just_counter: A flag indicating whether to just count the total results and don't get the data.
        - count_total_results: A flag indicating whether to count the total results.
        """
        self.manager = manager
        self.max_results = max_results
        self.order_by = order_by if order_by is not None else "uuid"
        self.order = order
        self.page_token = page_token
        self.just_counter = just_counter
        self.count_total_results = count_total_results

    def run(self) -> BasicList:
        """
        Executes the pagination logic and returns a BasicList object containing the paginated results.

        Returns:
        - BasicList: An object containing the paginated results, total results, next page token, previous page token, \
            and the number of items.
        """
        total_results = None
        if self.count_total_results or self.just_counter:
            total_results = self.manager.count()
        if self.just_counter:
            return BasicList(None, total_results=total_results)

        # Create compound ordering to ensure stable pagination
        if self.order_by:
            order_by = self.order_by
            if self.order == "desc":
                order_by = "-" + order_by
            # Always add uuid as secondary sort to ensure stable pagination
            if self.order == "desc":
                self.manager = self.manager.order_by(order_by, "-uuid")
            else:
                self.manager = self.manager.order_by(order_by, "uuid")
        else:
            # Default ordering
            if self.order == "desc":
                self.manager = self.manager.order_by("-uuid")
            else:
                self.manager = self.manager.order_by("uuid")

        if self.page_token:
            # Parse compound page token (format: "field_value|uuid")
            try:
                # Use rsplit so field values containing '|' don't corrupt the UUID part
                if "|" in self.page_token:
                    field_value, uuid_value = self.page_token.rsplit("|", 1)
                else:
                    # Fallback for old format
                    field_value = self.page_token
                    uuid_value = None

                # Create compound filter for stable pagination
                from django.db.models import Q

                if self.order == "desc":
                    # For descending: (field < value) OR (field = value AND uuid < uuid_value)
                    if uuid_value:
                        filter_condition = Q(
                            **{f"{self.order_by}__lt": field_value}
                        ) | Q(
                            **{f"{self.order_by}": field_value, "uuid__lt": uuid_value}
                        )
                    else:
                        filter_condition = Q(**{f"{self.order_by}__lt": field_value})
                else:
                    # For ascending: (field > value) OR (field = value AND uuid > uuid_value)
                    if uuid_value:
                        filter_condition = Q(
                            **{f"{self.order_by}__gt": field_value}
                        ) | Q(
                            **{f"{self.order_by}": field_value, "uuid__gt": uuid_value}
                        )
                    else:
                        filter_condition = Q(**{f"{self.order_by}__gt": field_value})

                self.manager = self.manager.filter(filter_condition)
            except (ValueError, AttributeError):
                # If page token is invalid, ignore it
                pass

        if self.max_results:
            self.manager = self.manager[: self.max_results]

        results = self.manager.all()
        results = list(results)

        # Handle pagination tokens for any field (direct or related)
        def get_field_value(obj, field_name):
            """Get field value using Django's field lookup mechanism"""
            try:
                # Try direct field access first
                if hasattr(obj, field_name):
                    return getattr(obj, field_name)

                # For related fields, use Django's field traversal
                parts = field_name.split("__")
                value = obj
                for part in parts:
                    if value is None:
                        return None
                    value = getattr(value, part, None)
                return value
            except (AttributeError, ValueError, TypeError):
                return None

        # Create compound page tokens
        def create_page_token(obj):
            if not obj:
                return None
            field_value = get_field_value(obj, self.order_by)
            if field_value is None:
                return None
            # Format: "field_value|uuid"
            return f"{field_value}|{obj.uuid}"

        return BasicList(
            items=results,
            total_results=total_results,
            next_page_token=create_page_token(results[-1]) if results else None,
            previous_page_token=create_page_token(results[0]) if results else None,
            number_of_items=len(results),
            manager=self.manager,
        )


def context_aware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            asyncio.get_running_loop()
            return sync_to_async(func, thread_sensitive=True)(*args, **kwargs)
        except RuntimeError:
            # Not in an async context
            return func(*args, **kwargs)

    return wrapper


class DataProvider:
    @staticmethod
    def users_accessible_for_user(
        user: "User",
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        max_results: Optional[int] = None,
        order_by: Optional[str] = None,
        page_token: Optional[str] = None,
        user_uuids: Optional[List[str]] = None,
    ) -> BasicList:
        """
        Get list of users that the given user has access to see.

        Access rules:
        - Admins/staff see everyone (delegates to `users`).
        - Non-admins
          - Themselves

        Args:
            user: The user requesting access.
            status: Filter by user status.
            is_active: Filter by active flag.
            search: Free-text search on name or email.
            max_results: Maximum number of results to return.
            order_by: Field to order by.
            page_token: Pagination token.
            user_uuids: If provided, returns intersection of accessible users AND
                        users in this list (used to check if specific users are accessible).

        This helper stays generic and composes the main `users` method so that
        pagination and future filters remain centralised.
        """
        # Admins/staff see everyone
        if user.is_staff or user.is_superuser:
            accessible_user_ids = user_uuids
        else:
            accessible_user_ids = [user.uuid]
        return DataProvider.users(
            status=status,
            is_active=is_active,
            search=search,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
            uuids=accessible_user_ids,
        )


    @staticmethod
    def user(
        uuid: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional["User"]:
        """
        Retrieves a user based on the provided filters.

        Parameters:
        - uuid (str, optional): The unique identifier of the user.

        Returns:
        - User: The user object that matches the provided filters, or None if no match is found.
        """
        from app.models.user import User

        user = User.objects
        if uuid is not None:
            user = user.filter(uuid=uuid)
        if email is not None:
            user = user.filter(email=email)

        return user.first()

    @staticmethod
    def users(
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        max_results: Optional[int] = None,
        order_by: Optional[str] = None,
        page_token: Optional[str] = None,
        uuids: Optional[list[str]] = None,
    ) -> BasicList:
        """
        Retrieves a list of users based on the provided filters.

        This is the generic entry point for user listings. More specialised helpers
        (like \"users_accessible_for_user\") should compose this method instead of
        duplicating pagination logic.

        Parameters:
        - status (str, optional): The status of the users to filter by.
        - is_active (bool, optional): Filter by active flag.
        - search (str, optional): Free-text search on name or email.
        - max_results (int, optional): The maximum number of results to return.
        - order_by (str, optional): The field to order the results by.
        - page_token (str, optional): The token for pagination.
        - uuids (list[str], optional): Limit results to this set of user UUIDs.

        Returns:
        - BasicList: A list of users that match the provided filters, along with pagination information.
        """
        from app.models.user import User

        users = User.objects

        if status:
            users = users.filter(status=status)
        if is_active is not None:
            users = users.filter(is_active=is_active)
        if uuids:
            users = users.filter(uuid__in=uuids)
        if search:
            from django.db.models import Q

            users = users.filter(Q(name__icontains=search) | Q(email__icontains=search))

        return Pager(
            manager=users,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
        ).run()

    @staticmethod
    def job(
        uuid: Optional[str] = None
    ) -> Optional["Job"]:
        """
        Retrieves a job based on the provided filters.

        Parameters:
        - uuid (str, optional): The unique identifier of the job.

        Returns:
        - Job: The job object that matches the provided filters, or None if no match is found.
        """
        from app.models.job import Job

        job = Job.objects
        if uuid is not None:
            job = job.filter(uuid=uuid)

        return job.first()

    @staticmethod
    def jobs(
        queue: Optional[str] = None,
        queues: Optional[List[str]] = None,
        exclude_queue: Optional[str] = None,
        exclude_queues: Optional[List[str]] = None,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        user_uuid: Optional[str] = None,
        max_results: Optional[int] = None,
        order_by: Optional[str] = None,
        page_token: Optional[str] = None,
        only_available: bool = False,
        payload_contains: Optional[dict] = None,
        just_counter: Optional[bool] = False,
    ) -> BasicList:
        """
        Retrieves a list of jobs based on the provided filters.

        Parameters:
        - queue (str, optional): The queue name of the jobs to filter by.
        - queues (List[str], optional): List of queue names to filter by.
        - exclude_queue (str, optional): A queue name to exclude from results.
        - exclude_queues (List[str], optional): List of queue names to exclude.
        - status (str, optional): The status  of the jobs to filter by.
        - payload_contains (dict, optional): JSON payload filter passed to payload__contains.
        - just_counter (bool, optional): If True, only count total results without loading items.
        - user_uuid (str, optional): The user UUID to filter by.
        - max_results (int, optional): The maximum number of results to return.
        - order_by (str, optional): The field to order the results by.
        - page_token (str, optional): The token for pagination.

        Returns:
        - BasicList: A list of jobs that match the provided filters, along with pagination information.
        """
        from app.models.job import Job

        # Initialize a QuerySet of Job objects
        jobs = Job.objects

        # Apply filters based on the provided parameters
        queue_filters: List[str] = []
        if queues:
            queue_filters.extend(queues)
        if queue:
            queue_filters.append(queue)
        if queue_filters:
            jobs = jobs.filter(queue__in=list(dict.fromkeys(queue_filters)))
        excluded_queue_filters: List[str] = []
        if exclude_queues:
            excluded_queue_filters.extend(exclude_queues)
        if exclude_queue:
            excluded_queue_filters.append(exclude_queue)
        if excluded_queue_filters:
            jobs = jobs.exclude(queue__in=list(dict.fromkeys(excluded_queue_filters)))
        if statuses:
            jobs = jobs.filter(status__in=statuses)
        elif status:
            jobs = jobs.filter(status=status)
        if user_uuid:
            jobs = jobs.filter(user_id=user_uuid)
        if payload_contains:
            jobs = jobs.filter(payload__contains=payload_contains)
        if only_available:
            from django.db.models import Q
            from django.utils import timezone

            jobs = jobs.filter(
                Q(available_at__isnull=True) | Q(available_at__lte=timezone.now())
            )

        # Use the Pager class to paginate the QuerySet and return the results
        return Pager(
            manager=jobs,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
            just_counter=just_counter,
        ).run()

    # ── API Keys ──────────────────────────────────────────────────────────

    @classmethod
    def api_key(
        cls,
        uuid: str | None = None,
        user=None,
    ):
        """
        Get a single API key by UUID or by owning user.

        Args:
            uuid: API key UUID.
            user: User instance -- returns the user's active key.

        Returns:
            ApiKey | None
        """
        from app.models.api_key import ApiKey

        if uuid:
            return ApiKey.objects.filter(uuid=uuid).first()
        if user is not None:
            return ApiKey.objects.filter(user=user).first()
        return None
