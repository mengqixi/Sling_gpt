from __future__ import annotations

from typing import Any


TEMPLATES = [
    ("hero-image", "白底/纯色底产品主图", "基础商品图", True, "2048x2048", "正面三分之二角度，干净背景，包袋完整清晰"),
    ("lifestyle-scene", "场景化生活图", "场景与模特", True, "1152x2048", "法式轻奢生活场景，自然使用女包"),
    ("flat-lay", "平铺图", "基础商品图", False, "2048x2048", "俯拍平铺，搭配少量精致配饰"),
    ("detail-macro", "细节微距图", "细节与信息", True, "2048x2048", "展示材质、车线、Logo和五金工艺"),
    ("poster-banner", "促销海报/Banner", "营销素材", False, "2048x1152", "留出标题和活动文案安全区"),
    ("social-media", "社交媒体素材", "营销素材", False, "2048x2048", "适合社交平台发布的轻奢视觉"),
    ("ugc-style", "UGC风格/买家秀", "场景与模特", False, "1152x2048", "真实自然的日常上身分享感"),
    ("model-showcase", "模特展示图", "场景与模特", True, "1152x2048", "法式女性模特展示真实上身比例"),
    ("before-after", "使用前后对比图", "营销素材", False, "2048x2048", "以造型搭配前后对比表达女包价值"),
    ("packaging", "包装设计展示", "品牌资产", False, "2048x2048", "女包、包装盒、防尘袋与吊牌完整展示"),
    ("infographic", "信息图/A+ Content", "细节与信息", True, "2048x2048", "结构化展示容量、材质和核心卖点"),
    ("creative-concept", "创意概念广告图", "营销素材", False, "2048x2048", "品牌感创意构图，产品仍是唯一主体"),
    ("size-spec", "尺寸规格+使用步骤图", "细节与信息", True, "2048x2048", "准确标注长宽高和容量参照"),
    ("multi-product", "多产品套装/组合展示", "基础商品图", False, "2048x2048", "同系列不同颜色或尺寸组合"),
    ("livestream", "电商直播间场景", "渠道素材", False, "2048x1152", "女包直播讲解场景，产品细节可见"),
    ("try-on-virtual", "虚拟试背/融入场景", "场景与模特", False, "1152x2048", "按真实尺寸将女包自然融入人物造型"),
    ("exploded-view", "技术拆解/爆炸图", "细节与信息", False, "2048x2048", "分层展示包体结构、内袋、肩带和五金"),
    ("ghost-mannequin", "隐形模特展示", "实验模板", False, "1152x2048", "无人物干扰地展示背负位置和肩带形态"),
    ("multi-angle-grid", "产品多角度网格", "基础商品图", True, "2048x2048", "正面、侧面、背面和俯视四宫格"),
    ("magazine-editorial", "杂志大片/封面", "场景与模特", True, "1152x2048", "法式轻奢杂志大片，保留排版安全区"),
    ("seasonal-campaign", "季节主题网格", "营销素材", False, "2048x2048", "围绕当季主题建立统一系列视觉"),
    ("luxury-atmospherics", "奢华氛围渲染", "品牌资产", True, "2048x2048", "浪漫轻奢氛围，克制道具和高级布光"),
    ("device-mockup", "设备界面模型", "实验模板", False, "2048x1152", "在品牌官网或社媒界面中展示女包视觉"),
    ("storefront", "店铺门面/空间摄影", "渠道素材", False, "2048x1152", "轻奢女包精品店橱窗或陈列空间"),
    ("sports-campaign", "运动/通勤活力广告", "实验模板", False, "1152x2048", "都市通勤与轻运动语境中的女包广告"),
]


def list_templates() -> list[dict[str, Any]]:
    return [
        {"id": item[0], "name": item[1], "category": item[2], "recommended": item[3], "default_size": item[4], "handbag_direction": item[5]}
        for item in TEMPLATES
    ]


def build_campaign_lock(data: dict[str, Any]) -> str:
    return "\n".join(
        [
            "【整组视觉锁定】",
            f"品牌定位：{data.get('brand_positioning') or 'ELLE箱包，法式轻奢、优雅、现代、浪漫但不过度装饰'}。",
            f"目标人群：{data.get('audience') or '重视质感与日常搭配的都市女性'}。",
            f"主色与视觉气质：{data.get('palette') or '黑、象牙白、酒红与低饱和金色点缀'}。",
            f"统一背景与光线：{data.get('visual_style') or '自然柔光、真实材质、精致但可用于电商销售的法式画面'}。",
            "同批图片必须保持相同的色彩体系、布光逻辑、品牌气质和产品比例。",
        ]
    )


def plan_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    selected = payload.get("template_ids") or []
    lookup = {item[0]: item for item in TEMPLATES}
    unknown = [item for item in selected if item not in lookup]
    if unknown:
        raise ValueError(f"未知模板：{', '.join(unknown)}")
    product = payload.get("product_name") or "上传图片中的ELLE女包"
    description = payload.get("product_description") or "严格依据参考图中的女包"
    selling_points = payload.get("selling_points") or "突出包型、材质、容量、五金与日常搭配价值"
    dimensions = payload.get("dimensions") or "按参考图保持真实比例，不夸大尺寸"
    platform = payload.get("platform") or "品牌电商详情页"
    copy_text = payload.get("copy_text") or "不生成无法核实的价格、销量、评价、认证或参数"
    extra = payload.get("extra_requirements") or ""
    lock = build_campaign_lock(payload)
    items = []
    sizes = payload.get("sizes") or {}
    for template_id in selected:
        item = lookup[template_id]
        prompt = "\n\n".join(
            part
            for part in [
                lock,
                "\n".join(
                    [
                        "【女包结构锁定】",
                        f"产品：{product}。{description}",
                        "严格保持参考图的包型轮廓、长宽比例、包盖与开口结构、肩带/手提/链条数量和连接方式。",
                        "严格保持参考图中的ELLE Logo位置、拼写和比例，并保持五金形状与颜色、拉链、缝线、压纹、图案和材质特征；不得改成其他品牌，不得凭空增加或删除配件。",
                        f"尺寸参考：{dimensions}。人物上身图必须遵守真实尺寸比例。",
                        "画面中女包必须完整、清晰且是视觉主体，不被手臂、衣服、头发、文字或道具遮挡关键结构。",
                    ]
                ),
                "\n".join(
                    [
                        f"【本张任务：{item[1]}】",
                        f"表现方向：{item[5]}。",
                        f"核心卖点：{selling_points}。",
                        f"使用渠道：{platform}。",
                        f"文案规则：{copy_text}。如需文字，使用简洁准确的中文并留出安全边距。",
                        "生成一张独立成图，不要在本张内部自动拼接多套不相关方案；除非本模板明确要求网格或信息图。",
                        "使用真实商业摄影质感，避免塑料感、错误Logo、畸形肩带、错误五金、乱码文字和不合理透视。",
                    ]
                ),
                f"【额外要求】\n{extra}" if extra.strip() else "",
            ]
            if part
        )
        items.append({"template_id": template_id, "name": item[1], "category": item[2], "image_size": sizes.get(template_id) or item[4], "final_prompt": prompt})
    return {"campaign_lock": lock, "count": len(items), "items": items}
