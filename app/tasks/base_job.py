from collections import defaultdict
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.job import Job


class BaseJob:
    class Meta:
        name = "base_job"

    @classmethod
    def get_job(cls, shuffle: bool = True) -> Optional["Job"]:
        """
        Retrieves a single available job from the queue.

        When shuffle=False the method falls back to returning the first candidate
        directly (used for deterministic testing or forced job execution).

        Args:
            shuffle: Whether to apply fair random selection. Defaults to True.

        Returns:
            Optional[Job]: A selected available job, or None if no jobs are ready.
        """
        import random
        from app.modules.provider.data_provider import DataProvider

        candidates = DataProvider.jobs(queue=cls.Meta.name, only_available=True).items
        if not candidates:
            return None

        # Recheck availability in Python in case the DB snapshot is slightly stale
        available = [j for j in candidates if j.is_available()]
        if not available:
            return None

        if not shuffle:
            return available[0]
        return random.choice(available)