from app.config.base_config import BaseConfig

class DeleteTemporaryFileConfig(BaseConfig):
    MAX_RETRIES: int = BaseConfig.env.int(
        "JOBS_DELETE_TEMPORARY_FILE_MAX_RETRIES", default=2
    )
    DELAY_TO_RETRY_FAILED_JOBS = BaseConfig.env.int(
        "JOBS_DELETE_TEMPORARY_FILE_DELAY_TO_RETRY_FAILED_JOBS", default=2
    )
