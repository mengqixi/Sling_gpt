# 开发说明

后端启动入口是 `backend.app:app`。启动时会执行：

1. `init_db()` 创建表和默认 API 配置。
2. `seed_prompt_templates()` 从 `backend/prompts` 导入三份系统提示词。

中转站适配器在 `backend/services/relay_image_service.py`，只使用 `requests`，不依赖 OpenAI SDK。

提示词渲染在 `backend/services/prompt_service.py`：

1. 先替换 `{{变量名}}`。
2. 再替换中文占位符。
3. 最后把 `extra_requirements` 追加到末尾。

上传图片当前只校验格式，不做 20MB 限制。
