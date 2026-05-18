from celery import Celery
from app.config.celery import CeleryConfig
from app.utils.string_util import StringUtil
import yaml
import logging.config
from app.utils.log_util import LogUtil
from app.config.app import AppConfig
import os

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", AppConfig.SETTINGS_MODULE)

# Initialize Celery instance
celery = Celery(__name__, broker=CeleryConfig.BROKER_URL)
celery.conf.update(worker_prefetch_multiplier=1)

# Initialize logger
base_dir = AppConfig.BASE_DIR
with open(f"{base_dir}/log_conf.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

logger = LogUtil.get_logger()
logger.info(f"---- Celery Workers Started ({__name__})-----")

# Autodiscover tasks
celery.autodiscover_tasks(
    [
        "app.tasks.delete_temporary_file",
    ],
    force=True,
)

# Generate a unique hash prefix for worker processes
worker_hash_prefix = StringUtil.random_string(10)
os.environ.setdefault("WORKER_HASH_PREFIX", worker_hash_prefix)


# Setup periodic tasks
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from celery.schedules import crontab

    # Import and schedule other periodic tasks

    # Schedule other periodic tasks

    # sender.add_periodic_task(30, send_message_task)
    