from ayon_server.settings import (
    BaseSettingsModel, 
    SettingsField
    )

DEFAULT_VALUES = {}


class MySettings(BaseSettingsModel):
    scripts_hot_directory: str = SettingsField(
        "",
        title="Scripts hot directory",
        description="Path to a directory on disk that contains studio moulinettes"
    )
