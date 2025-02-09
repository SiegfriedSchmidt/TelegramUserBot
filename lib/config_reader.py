from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, JsonConfigSettingsSource
from pydantic import SecretStr
from typing import List, Type, Tuple

from lib.init import secret_folder_path

json_path = secret_folder_path / 'settings.json'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(json_file=json_path, json_file_encoding='utf-8', extra='allow')
    telegram_api_id: SecretStr
    telegram_api_hash: SecretStr
    telegram_channel: SecretStr
    telegram_admins: List[str]
    openrouter_api_keys: List[SecretStr]

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            env_settings,
            file_secret_settings,
        )


config = Settings()
