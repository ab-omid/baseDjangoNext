from app.config.base_config import BaseConfig


class OpenAiConfig(BaseConfig):
    API_KEY: str = BaseConfig.env.str("OPENAI_API_KEY", default=None)
    MODEL: str = BaseConfig.env.str("OPEN_AI_MODEL", default='gpt-4-turbo')
    TRANSCRIPT_MODEL: str = BaseConfig.env.str("OPEN_AI_TRANSCRIPT_MODEL", default='whisper-1')