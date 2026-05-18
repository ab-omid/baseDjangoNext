"""
Pytest configuration. Set DJANGO_SETTINGS_MODULE before any Django imports.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PDNR.settings")
