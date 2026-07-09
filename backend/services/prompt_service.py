import json
import re
from typing import Any

from ..database import db_session, now_iso


CHINESE_PLACEHOLDERS = {
    "color_change": {"\u3010\u586b\u5199\u76ee\u6807\u989c\u8272\u3011": "target_color"},
    "material_replace": {"\u3010\u586b\u5199\u76ee\u6807\u6750\u8d28\u3011": "target_material"},
    "model_showcase": {"\u3010\u586b\u5199\u6a21\u7279\u5c55\u793a\u8981\u6c42\u3011": "model_showcase_requirement"},
}


def render_prompt(template_content: str, task_type: str, params: dict[str, Any]) -> str:
    prompt = (template_content or "").lstrip("\ufeff")
    for key, value in params.items():
        prompt = prompt.replace("{{" + key + "}}", str(value or ""))
    prompt = re.sub(r"{{\s*([a-zA-Z0-9_]+)\s*}}", "", prompt)
    for placeholder, key in CHINESE_PLACEHOLDERS.get(task_type, {}).items():
        prompt = prompt.replace(placeholder, str(params.get(key) or ""))

    extra = str(params.get("extra_requirements") or "").strip()
    if extra and extra not in prompt:
        prompt = prompt.rstrip() + "\n\n\u989d\u5916\u8981\u6c42\uff1a\n" + extra
    return prompt.strip()


def render_prompt_by_template(template_id: int | None, task_type: str, params: dict[str, Any]) -> str:
    with db_session() as conn:
        if template_id:
            row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM prompt_templates WHERE task_type = ? AND is_default = 1 ORDER BY id LIMIT 1",
                (task_type,),
            ).fetchone()
        if not row:
            raise ValueError("\u6ca1\u6709\u627e\u5230\u53ef\u7528\u63d0\u793a\u8bcd\u6a21\u677f")
        return render_prompt(row["template_content"], task_type, params)


def row_to_prompt(row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "task_type": row["task_type"],
        "template_content": (row["template_content"] or "").lstrip("\ufeff"),
        "variables": json.loads(row["variables_json"] or "[]"),
        "is_default": bool(row["is_default"]),
        "is_system": bool(row["is_system"]),
        "original_file_name": row["original_file_name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def set_default_prompt(template_id: int) -> None:
    with db_session() as conn:
        row = conn.execute("SELECT task_type FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()
        if not row:
            raise ValueError("\u63d0\u793a\u8bcd\u6a21\u677f\u4e0d\u5b58\u5728")
        conn.execute("UPDATE prompt_templates SET is_default = 0 WHERE task_type = ?", (row["task_type"],))
        conn.execute(
            "UPDATE prompt_templates SET is_default = 1, updated_at = ? WHERE id = ?",
            (now_iso(), template_id),
        )
