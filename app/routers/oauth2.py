from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credentialexception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_user = str(payload.get("user_id"))
        print(type(id_user))
        if id_user is None:
            raise credentialexception
        token_data = schemas.TokenData(id=id_user)
    except JWTError as e:
        raise credentialexception from e
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentialexception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="could not validate credentials",
                                        headers={"WWW-Authenticate": "Bearer"})
    return verify_access_token(token, credentialexception)
