import environ
import os


class BaseConfig:
    env = environ.Env(DEBUG=(bool, False))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
