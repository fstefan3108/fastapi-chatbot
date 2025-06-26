from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.config import settings
from app.db.session import LocalSession


### Database session initialization ###

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# db_dependency instantiation #
db_dependency = Annotated[Session, Depends(get_db)]

### Gets the current logged user by decoding the JWT token; ###
### Extracts user's username and ID from the JWT package, using provided key and algorithm. ###

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        return {"username": username, "id": user_id}
    except JWTError:
            raise HTTPException(status_code=401, detail="Invalid Credentials")


# User dependency instantiation #
user_dependency = Annotated[dict, Depends(get_current_user)]