from fastapi import APIRouter, File, HTTPException, UploadFile

from ..services.file_service import save_upload

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
def upload_image(file: UploadFile = File(...)):
    try:
        return save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
