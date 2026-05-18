import logging

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver


logger = logging.getLogger(__name__)