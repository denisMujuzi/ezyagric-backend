# check token in header and decode and verify it
from typing import Annotated
from fastapi import Header, HTTPException
import jwt
from utils import settings
from zoneinfo import ZoneInfo

nairobi_tz = ZoneInfo("Africa/Nairobi")

# decode and verify JWT token
async def decode_jwt(auth_header: str) -> int:
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    # Accept format: "JWT <token>"
    parts = auth_header.split()
    token = auth_header
    if len(parts) == 2 and parts[0] == "JWT":
        token = parts[1]
    elif len(parts) > 1:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format. Expected 'JWT <token>'")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        farmer_id = payload.get("sub")
        return farmer_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_token(token: Annotated[str, Header()]) -> int:
    farmer_id = await decode_jwt(token)
    return int(farmer_id)