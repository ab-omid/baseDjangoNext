from __future__ import absolute_import

from typing import TYPE_CHECKING
from PDNR.celery import celery
from app.tasks.base_job import BaseJob
from app.tasks.base_task import BaseTask
from datetime import timedelta

from django.utils import timezone

if TYPE_CHECKING:
    from app.models.job import Job


class DeleteTemporaryFileJob(BaseJob):
    """
    A class to manage the deletion of temporary files.
    """

    class Fields:
        path = "path"

    class Meta:
        name = "delete_temporary_file"

    @staticmethod
    def create_new_job(path: str, delay_in_seconds: int) -> "Job":
        from app.models.job import Job

        job = Job()
        job.queue = DeleteTemporaryFileJob.Meta.name
        job.status = Job.STATUSES.TODO.value
        job.set_payload_field(DeleteTemporaryFileJob.Fields.path, path)
        job.set_available_at(timezone.now() + timedelta(seconds=delay_in_seconds))
        job.save()
        return job

    @staticmethod
    def success(job: "Job"):
        job.hard_delete()


@celery.task(name="delete_temporary_file", bind=True, base=BaseTask)
def delete_temporary_file_task(self, job_id: str = None):
    from app.modules.provider.data_provider import DataProvider
    from app.models.job import Job

    if job_id is None:
        job = DeleteTemporaryFileJob.get_job()

    else:
        job = DataProvider.job(uuid=job_id)

    if job is not None and isinstance(job, Job):
        job.start()
        try:
            path = job.get_payload_field(DeleteTemporaryFileJob.Fields.path)
            if path is None:
                job.fail("Path parameter is required")
                return

            from django.core.files.storage import default_storage

            if default_storage.exists(path):
                default_storage.delete(path)

            DeleteTemporaryFileJob.success(job)
        except Exception as e:
            from app.config.jobs import DeleteTemporaryFileConfig
            import traceback

            traceback_string = traceback.format_exc()
            job.retry(
                max_retries=DeleteTemporaryFileConfig.MAX_RETRIES,
                delay_in_minutes=DeleteTemporaryFileConfig.DELAY_TO_RETRY_FAILED_JOBS,
                message=repr(e) + traceback_string,
            )
