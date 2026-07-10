from time import perf_counter

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.api_config_service import get_config
from ..services.file_service import crop_generated_image, save_existing_image_as_upload, split_image_grid
from ..services.image_job_service import (
    add_generated_image,
    create_job,
    get_generated_image,
    get_job,
    get_upload,
    replace_grid_split_images,
    set_job_status,
)
from ..services.relay_image_service import call_relay_image_api, save_images_from_response

router = APIRouter(prefix="/api", tags=["generate"])


class GeneratePayload(BaseModel):
    task_type: str
    uploaded_image_id: int | None = None
    uploaded_image_ids: list[int] | None = None
    prompt_template_id: int | None = None
    final_prompt: str
    api_config_id: int
    output_count: int | None = None
    image_size: str = "1024x1024"
    quality: str | None = None
    params: dict = {}


class CropPayload(BaseModel):
    left: float
    top: float
    right: float
    bottom: float


@router.post("/generate")
def generate(payload: GeneratePayload):
    upload_ids = payload.uploaded_image_ids or ([payload.uploaded_image_id] if payload.uploaded_image_id else [])
    upload_ids = [image_id for image_id in upload_ids if image_id]
    if not upload_ids:
        raise HTTPException(status_code=400, detail="请先上传女包原图")
    uploads = []
    for image_id in upload_ids:
        upload_row = get_upload(image_id)
        if not upload_row:
            raise HTTPException(status_code=404, detail=f"上传图片不存在：{image_id}")
        uploads.append(upload_row)
    upload = uploads[0]
    config = get_config(payload.api_config_id, include_secret=True)
    if not config:
        raise HTTPException(status_code=404, detail="API 配置不存在")
    if not config.get("enabled"):
        raise HTTPException(status_code=400, detail="API 配置未启用")
    if not payload.final_prompt.strip():
        raise HTTPException(status_code=400, detail="最终提示词不能为空")

    job_id = create_job(payload.model_dump(), upload, config)
    set_job_status(job_id, "running")
    started = perf_counter()
    try:
        response_json = call_relay_image_api(
            config,
            [item["file_path"] for item in uploads],
            payload.final_prompt,
            payload.output_count,
            payload.image_size,
            payload.quality,
        )
        saved_images = save_images_from_response(response_json, config, job_id)
        auto_split = bool((payload.params or {}).get("auto_split_grid", False))
        if auto_split and len(saved_images) == 1:
            try:
                split_paths = split_image_grid(saved_images[0]["path"], job_id)
                for path in split_paths:
                    add_generated_image(job_id, path, "split_grid")
            except Exception:
                add_generated_image(job_id, saved_images[0]["path"], saved_images[0]["source_type"])
        else:
            for item in saved_images:
                add_generated_image(job_id, item["path"], item["source_type"])
        set_job_status(job_id, "success", response_json=response_json)
    except Exception as exc:
        elapsed = round(perf_counter() - started, 1)
        set_job_status(job_id, "failed", error_message=f"{exc}（本次请求耗时 {elapsed} 秒）")
    job = get_job(job_id)
    return {"job_id": job_id, "status": job["status"], "job": job}


@router.get("/jobs/{job_id}")
def read_job(job_id: int):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job


@router.post("/generated-images/{image_id}/reuse")
def reuse_generated_image(image_id: int):
    image = get_generated_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="生成图片不存在")
    try:
        return save_existing_image_as_upload(image["image_path"], file_name=f"continue_from_{image_id}.png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/generated-images/{image_id}/split-grid")
def split_generated_grid(image_id: int):
    image = get_generated_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="生成图片不存在")
    try:
        paths = split_image_grid(image["image_path"], image["job_id"])
        replace_grid_split_images(image["job_id"], image_id, paths)
        return {"job": get_job(image["job_id"])}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/generated-images/{image_id}/crop")
def crop_generated(image_id: int, payload: CropPayload):
    image = get_generated_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="生成图片不存在")
    try:
        path = crop_generated_image(image["image_path"], image["job_id"], payload.left, payload.top, payload.right, payload.bottom)
        add_generated_image(image["job_id"], path, f"manual_crop:{image_id}")
        return {"job": get_job(image["job_id"])}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
