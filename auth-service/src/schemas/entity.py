from pydantic import BaseModel, EmailStr, model_validator


class SuccessfulLogout(BaseModel):
    detail: str


class DeviceFingerprint(BaseModel):
    user_agent: str
    screen_width: int
    screen_height: int
    timezone: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: DeviceFingerprint


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    device_fingerprint: DeviceFingerprint


class SuccessfulAuth(BaseModel):
    access_token: str
    refresh_token: str


class UserLoginHistory(BaseModel):
    historical_points: list[DeviceFingerprint]

    class Config:
        from_attributes = True


class VerificationTOTP(BaseModel):
    token: str


class UserInfo(BaseModel):
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str
    old_password: str
    new_password: str
    new_password_confirmation: str

    @model_validator(mode='after')
    def check_passwords(self):
        old_pass = self.old_password
        new_pass = self.new_password
        if old_pass is None and new_pass is not None:
            raise ValueError('You must provide old password to proceed change.')
        if old_pass is not None and new_pass is None:
            raise ValueError('You must provide previous and new passwords.')
        return self

    @model_validator(mode='after')
    def check_new_passwords_match(self):
        new_pass = self.new_password
        validation = self.new_password_confirmation
        if new_pass is not None and validation is not None and new_pass != validation:
            raise ValueError('Passwords must match.')
        if new_pass is None and validation is not None or new_pass is not None and validation is None:
            raise ValueError('You must provide both passwords.')
        return self
