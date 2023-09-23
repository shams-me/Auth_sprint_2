import enum


class LoginProviderSelect(str, enum.Enum):
    yandex: str = "yandex"
    google: str = "google"
