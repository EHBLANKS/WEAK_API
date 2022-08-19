import jwt
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    HTTPBasicCredentials,
)
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Local Imports
from api.utils.database import get_db
from api.meta.database.model import User
from api.meta.constants.errors import SIGNATURE_EXPIRED, INVALID_TOKEN
from api.config import get_settings
from api.meta.constants.errors import USER_DOES_NOT_EXIST

# -----------------------
settings = get_settings()
# -----------------------


auth_header = HTTPBearer()


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
            # two hour token for the workshop duration
            "exp": datetime.utcnow() + timedelta(hours=2),
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


def require_authentication(
    Authorization: HTTPBasicCredentials = Depends(auth_header),
):
    auth_handler = AuthHandler()
    token = str(Authorization.credentials)
    decoded_token = auth_handler.decode_token(token)

    return decoded_token


def require_user_account(
    auth: dict = Depends(require_authentication),
    db: Session = Depends(get_db),
) -> User:
    """Given a firebase auth token, returns the user account information"""

    # Get user_id from firebase auth UID
    userInfo = db.query(User).filter(User.id == auth["id"]).first()

    if userInfo is None:
        raise HTTPException(
            status_code=403,
            detail=USER_DOES_NOT_EXIST,
            headers={"Authorization": auth},
        )

    return userInfo
