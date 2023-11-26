import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from ..libs.b2 import b2_upload_file
from ..security import get_current_user
from .. import User
from typing import Annotated

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Uploading a file")

    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name

            logger.info("Saving uploaded file temporarily to %s", filename)

            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            file_url = b2_upload_file(local_file=filename, file_name=file.filename)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        ) from exc

    return {"detail": f"Successfuly uploaded {file.filename}", "file_url": file_url}
