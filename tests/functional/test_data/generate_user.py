from tests.functional.utils.user_fields import DEFAULT_USER_PASSWORD, DEFAULT_USERNAME


def generate_user_registration_body(email: str):
    return {
        "email": email,
        "username": DEFAULT_USERNAME,
        "password": DEFAULT_USER_PASSWORD,
        "device_fingerprint": {
            "user_agent": "MacOS", "screen_width": 720, "screen_height": 720, "timezone": "Asia/Tokyo"
        }
    }


def generate_user_login_body(email: str, password: str = DEFAULT_USER_PASSWORD):
    return {
        "email": email,
        "password": password,
        "device_fingerprint": {
            "user_agent": "MacOS", "screen_width": 720, "screen_height": 720, "timezone": "Asia/Tokyo"
        }
    }
