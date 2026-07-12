from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.ecommerce_service import list_templates, plan_campaign

router = APIRouter(prefix="/api/ecommerce", tags=["ecommerce"])


class EcommercePlanPayload(BaseModel):
    template_ids: list[str] = Field(default_factory=list)
    product_name: str = ""
    product_description: str = ""
    selling_points: str = ""
    dimensions: str = ""
    platform: str = "品牌电商详情页"
    brand_positioning: str = "ELLE箱包，法式轻奢、优雅、现代、浪漫"
    audience: str = "都市女性"
    palette: str = ""
    visual_style: str = ""
    copy_text: str = ""
    extra_requirements: str = ""
    sizes: dict[str, str] = Field(default_factory=dict)


@router.get("/templates")
def templates():
    return list_templates()


@router.post("/plan")
def plan(payload: EcommercePlanPayload):
    if not payload.template_ids:
        raise HTTPException(status_code=400, detail="请至少选择一个电商图片模板")
    try:
        return plan_campaign(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
