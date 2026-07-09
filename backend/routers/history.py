from fastapi import APIRouter, HTTPException

from ..services.image_job_service import delete_job, list_history

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def history(task_type: str | None = None, status: str | None = None, date_from: str | None = None, date_to: str | None = None):
    return list_history({"task_type": task_type, "status": status, "date_from": date_from, "date_to": date_to})


@router.delete("/jobs/{job_id}")
def remove_job(job_id: int):
    if not delete_job(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"ok": True}
