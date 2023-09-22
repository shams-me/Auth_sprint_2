from hashlib import sha256 as hash_function
from abc import ABC, abstractmethod
from fastapi import HTTPException, status
import jwt
from jwt import ExpiredSignatureError, DecodeError, InvalidTokenError


class ITokenEncoder(ABC):

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self._secret = secret
        self._algorithm = algorithm

    @abstractmethod
    def encode(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode(self, token: str) -> dict:
        raise NotImplementedError


class JWTEncoder(ITokenEncoder):

    def encode(self, payload: dict) -> str:
        user_id = payload.get('user_id')
        if user_id:
            secret = self._generate_dynamic_nonce(user_id)
            return jwt.encode(payload=payload, key=secret, algorithm=self._algorithm)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id not found in payload")

    def decode(self, token: str) -> dict:
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            user_id = unverified_payload.get('user_id')
            if user_id:
                secret = self._generate_dynamic_nonce(user_id)
                return jwt.decode(token, secret, algorithms=[self._algorithm])
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
        except DecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token could not be decoded.")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def _generate_dynamic_nonce(self, user_id: str):
        return hash_function((self._secret + user_id).encode('utf-8')).hexdigest()
