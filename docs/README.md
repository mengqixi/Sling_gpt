# 女包 AI 生图工具

这是给设计师内部使用的女包 AI 生图网站。设计师上传女包原图后，可以选择包身换色、材质替换、模特展示图，系统根据模板生成提示词初稿，设计师可以在前端继续修改颜色、五金、风格、构图等要求，最后通过可配置中转站 API 生成图片并保存历史。

## 功能列表

- 上传 jpg、jpeg、png、webp 原图，当前不限制 20MB。
- 包身换色、材质替换、模特展示图三类任务。
- 三份系统提示词初始化到数据库。
- 生成页可临时编辑最终提示词。
- 提示词管理页可编辑、保存、另存、复制、恢复系统模板、设置默认模板。
- API 设置页可配置中转站 Base URL、模型、路径、字段名、认证方式、返回字段路径。
- API Key 只保存到后端，前端列表只显示掩码。
- 支持 `multipart/form-data` 和 `application/json` 请求。
- 支持 base64 和 URL 图片返回。
- 支持历史记录、图片展示、下载和删除任务。

## 技术栈

- 后端：FastAPI、SQLite、requests、Pillow
- 前端：React、Vite、TypeScript
- 数据库：`data/app.db`

## 目录结构

```text
backend/
  app.py
  database.py
  seed_prompts.py
  routers/
  services/
  prompts/
  uploads/
  results/
frontend/
  src/
data/
docs/
requirements.txt
```

## 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install
```

## 启动后端

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

后端启动时会自动创建 SQLite 表、`backend/uploads`、`backend/results`，并把三份提示词写入 `prompt_templates`。

## 启动前端

```powershell
cd frontend
npm run dev
```

打开：

```text
http://127.0.0.1:5173
```

## 配置中转站 API

进入“API 设置”，编辑或新增配置：

- `API Base URL`：中转站域名，例如 `https://your-relay-domain.com`
- `接口路径`：例如 `/v1/images/edits`
- `请求内容类型`：`multipart/form-data` 或 `application/json`
- `图片字段名`：默认 `image`
- `提示词字段名`：默认 `prompt`
- `模型字段名`：默认 `model`
- `输出张数字段名`：默认 `n`
- `尺寸字段名`：默认 `size`
- `质量字段名`：默认 `quality`
- `额外参数 JSON`：例如 `{"response_format":"b64_json"}`
- `返回图片类型`：`base64` 或 `url`
- `返回图片字段路径`：例如 `data.0.b64_json`、`data.*.b64_json`、`data.*.url`、`images.*`

如果中转站返回 URL，把返回图片类型改为 `url`，字段路径改为实际 URL 所在位置。后端会下载图片到 `backend/results` 再返回本地访问地址。

## 返回图片字段路径

当前支持：

- 点路径：`data.0.b64_json`
- 通配数组：`data.*.b64_json`
- 数组本身：`images.*`
- 嵌套数组路径：`choices.0.message.images.*`

## 使用流程

1. 在“生成”页上传女包原图。
2. 选择包身换色、材质替换或模特展示图。
3. 填写目标颜色、材质、模特展示要求等参数。
4. 选择提示词模板，点击“重新渲染”生成提示词初稿。
5. 在“最终提示词”文本框中按需修改颜色、五金、风格和其他要求。
6. 选择 API 配置，点击“开始生成”。
7. 在右侧查看结果图片并下载。
8. 在“历史记录”页查看生成记录。

## 常见错误

- `未配置 API Key`：进入 API 设置保存中转站密钥。
- `API Base URL 为空`：填写中转站域名。
- `接口路径为空`：填写实际接口路径。
- `中转站返回非 JSON`：检查中转站是否返回 JSON。
- `没有找到 data.0.b64_json`：检查“返回图片字段路径”是否匹配中转站响应。
- `base64 图片解码失败`：检查返回图片类型是否应该设置为 URL。
- `图片 URL 下载失败`：检查 URL 是否可访问。
