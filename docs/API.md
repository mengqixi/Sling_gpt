# API 概览

基础地址：`http://127.0.0.1:8000`

## 健康检查

`GET /api/health`

## 上传图片

`POST /api/upload`

表单字段：`file`

## 提示词模板

- `GET /api/prompts?task_type=color_change`
- `POST /api/prompts`
- `PATCH /api/prompts/{id}`
- `DELETE /api/prompts/{id}`
- `POST /api/prompts/{id}/set-default`
- `POST /api/prompts/{id}/restore`
- `POST /api/prompts/render`

## API 配置

- `GET /api/api-configs`
- `POST /api/api-configs`
- `PATCH /api/api-configs/{id}`
- `DELETE /api/api-configs/{id}`
- `POST /api/api-configs/{id}/set-default`
- `POST /api/api-configs/{id}/test`

`GET /api/api-configs` 不返回明文 `api_key`，只返回 `api_key_masked`。

## 生成任务

`POST /api/generate`

```json
{
  "task_type": "color_change",
  "uploaded_image_id": 1,
  "prompt_template_id": 1,
  "final_prompt": "最终提示词",
  "api_config_id": 1,
  "output_count": 4,
  "image_size": "1024x1024",
  "quality": "medium",
  "params": {
    "target_color": "黑色",
    "extra_requirements": ""
  }
}
```

## 任务与历史

- `GET /api/jobs/{id}`
- `GET /api/history`
- `DELETE /api/jobs/{id}`
