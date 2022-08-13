import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from api.meta.constants.errors import SIGNATURE_EXPIRED, INVALID_TOKEN
from api.config import get_settings

# -----------------------
settings = get_settings()
# -----------------------


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = settings.SECRET

    def get_password_hash(
        self,
        password: str,
    ) -> str:
        return self.pwd_context.hash(password)

    def verify_password(
        self,
        plain_password,
        hashed_password,
    ) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(
        self,
        user_id,
    ) -> str:
        "Creates a JWT token"

        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, minutes=5),
            "iat": datetime.utcnow(),
            "id": user_id,
        }

        return jwt.encode(
            payload=payload,
            key=self.secret,
            algorithm="HS256",
        )

    def decode_token(
        self,
        token: str,
    ) -> str:
        "Decodes a JWT token"

        # Decode token
        try:
            payload = jwt.decode(
                jwt=token,
                key=self.secret,
                algorithms=["HS256"],
            )
            return payload

        # Expired signature
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=SIGNATURE_EXPIRED,
            )
        # Invalid token
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN,
            )

    def auth_wrapper(
        self,
        auth: HTTPAuthorizationCredentials = Security(security),
    ) -> str:
        return self.decode_token(auth.credentials)
