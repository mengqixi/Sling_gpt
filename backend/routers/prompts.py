import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import db_session, now_iso
from ..seed_prompts import restore_system_prompt
from ..services.prompt_service import render_prompt_by_template, row_to_prompt, set_default_prompt

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptPayload(BaseModel):
    name: str
    task_type: str
    template_content: str
    variables: list[str] = []
    is_default: bool = False


class PromptPatch(BaseModel):
    name: str | None = None
    task_type: str | None = None
    template_content: str | None = None
    variables: list[str] | None = None
    is_default: bool | None = None


class RenderPayload(BaseModel):
    template_id: int | None = None
    task_type: str
    params: dict = {}


@router.get("")
def list_prompts(task_type: str | None = None):
    with db_session() as conn:
        if task_type:
            rows = conn.execute(
                "SELECT * FROM prompt_templates WHERE task_type = ? ORDER BY is_default DESC, id DESC",
                (task_type,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM prompt_templates ORDER BY task_type, is_default DESC, id DESC").fetchall()
        return [row_to_prompt(row) for row in rows]


@router.post("")
def create_prompt(payload: PromptPayload):
    ts = now_iso()
    with db_session() as conn:
        if payload.is_default:
            conn.execute("UPDATE prompt_templates SET is_default = 0 WHERE task_type = ?", (payload.task_type,))
        cursor = conn.execute(
            """
            INSERT INTO prompt_templates (
                name, task_type, template_content, variables_json, is_default,
                is_system, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                payload.name,
                payload.task_type,
                payload.template_content,
                json.dumps(payload.variables, ensure_ascii=False),
                1 if payload.is_default else 0,
                ts,
                ts,
            ),
        )
        row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_prompt(row)


@router.patch("/{template_id}")
def update_prompt(template_id: int, payload: PromptPatch):
    updates = []
    values = []
    data = payload.model_dump(exclude_unset=True)
    if "variables" in data:
        data["variables_json"] = json.dumps(data.pop("variables") or [], ensure_ascii=False)
    is_default = data.pop("is_default", None)
    for key, value in data.items():
        updates.append(f"{key} = ?")
        values.append(value)
    if is_default is not None:
        updates.append("is_default = ?")
        values.append(1 if is_default else 0)
    if not updates:
        raise HTTPException(status_code=400, detail="没有需要修改的字段")
    updates.append("updated_at = ?")
    values.append(now_iso())
    with db_session() as conn:
        row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="提示词模板不存在")
        if is_default:
            conn.execute("UPDATE prompt_templates SET is_default = 0 WHERE task_type = ?", (row["task_type"],))
        conn.execute(f"UPDATE prompt_templates SET {', '.join(updates)} WHERE id = ?", [*values, template_id])
        updated = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()
        return row_to_prompt(updated)


@router.delete("/{template_id}")
def delete_prompt(template_id: int):
    with db_session() as conn:
        row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="提示词模板不存在")
        if row["is_system"]:
            raise HTTPException(status_code=400, detail="系统模板不允许删除，请使用恢复默认")
        conn.execute("DELETE FROM prompt_templates WHERE id = ?", (template_id,))
        return {"ok": True}


@router.post("/{template_id}/set-default")
def set_prompt_default(template_id: int):
    try:
        set_default_prompt(template_id)
        return {"ok": True}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/restore")
def restore_prompt(template_id: int):
    if not restore_system_prompt(template_id):
        raise HTTPException(status_code=404, detail="系统模板不存在或原始文件缺失")
    return {"ok": True}


@router.post("/render")
def render_prompt(payload: RenderPayload):
    try:
        final_prompt = render_prompt_by_template(payload.template_id, payload.task_type, payload.params)
        return {"final_prompt": final_prompt}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
