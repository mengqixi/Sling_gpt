import { Save, TestTube2, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";

const defaults = {
  config_name: "默认中转站配置",
  api_base_url: "https://your-relay-domain.com",
  api_key: "",
  model_name: "gpt-image-2",
  endpoint_path: "/v1/images/edits",
  method: "POST",
  request_content_type: "multipart/form-data",
  auth_type: "bearer",
  auth_header_name: "Authorization",
  auth_header_prefix: "Bearer",
  image_field_name: "image",
  prompt_field_name: "prompt",
  model_field_name: "model",
  count_field_name: "n",
  size_field_name: "size",
  quality_field_name: "quality",
  extra_params_json: "{}",
  response_image_type: "base64",
  response_image_path: "data.0.b64_json",
  timeout_seconds: 300,
  enabled: true,
  is_default: false
};

export default function ApiConfigs() {
  const [items, setItems] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const rows = await api.getApiConfigs();
    setItems(rows);
    setSelected(rows[0] || defaults);
  }

  async function save() {
    const payload = { ...selected };
    delete payload.id;
    delete payload.api_key_masked;
    delete payload.created_at;
    delete payload.updated_at;
    if (!payload.api_key) {
      delete payload.api_key;
    }
    if (selected.id) {
      const updated = await api.updateApiConfig(selected.id, payload);
      setSelected(updated);
      setMessage("已保存 API 配置");
    } else {
      const created = await api.createApiConfig(payload);
      setSelected(created);
      setMessage("已新增 API 配置");
    }
    await load();
  }

  async function remove() {
    if (!selected?.id) return;
    await api.deleteApiConfig(selected.id);
    setMessage("已删除 API 配置");
    await load();
  }

  async function test() {
    if (!selected?.id) {
      setMessage("请先保存配置再测试");
      return;
    }
    const result = await api.testApiConfig(selected.id);
    setMessage(result.message || "测试完成");
  }

  function update(key: string, value: any) {
    setSelected({ ...selected, [key]: value });
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>API 设置</h1>
        <p>中转站接口、字段名、返回路径都从这里配置；前端只显示密钥掩码。</p>
      </header>
      <div className="manage-layout">
        <section className="panel list-panel">
          <div className="panel-title-row">
            <h2>配置列表</h2>
            <button onClick={() => setSelected({ ...defaults, config_name: "新中转站配置" })}>新增</button>
          </div>
          <div className="template-list">
            {items.map((item) => (
              <button key={item.id} className={selected?.id === item.id ? "selected" : ""} onClick={() => setSelected(item)}>
                <strong>{item.config_name}</strong>
                <span>
                  {item.model_name} {item.is_default ? "默认" : ""} {item.enabled ? "启用" : "停用"}
                </span>
                <small>{item.api_key_masked || "未配置 Key"}</small>
              </button>
            ))}
          </div>
        </section>
        <section className="panel editor-panel">
          {selected && (
            <>
              <div className="panel-title-row">
                <h2>编辑配置</h2>
                <div className="toolbar compact">
                  <button onClick={test}>
                    <TestTube2 size={16} />
                    测试
                  </button>
                  {selected.id && (
                    <button onClick={remove}>
                      <Trash2 size={16} />
                      删除
                    </button>
                  )}
                  <button className="primary" onClick={save}>
                    <Save size={16} />
                    保存
                  </button>
                </div>
              </div>
              {message && <div className="notice">{message}</div>}
              <div className="form-grid">
                <Input label="配置名称" value={selected.config_name || ""} onChange={(v) => update("config_name", v)} />
                <Input label="API Base URL" value={selected.api_base_url || ""} onChange={(v) => update("api_base_url", v)} />
                <Input label="API Key" type="password" placeholder={selected.api_key_masked || "输入后保存"} value={selected.api_key || ""} onChange={(v) => update("api_key", v)} />
                <Input label="模型名称" value={selected.model_name || ""} onChange={(v) => update("model_name", v)} />
                <Input label="接口路径" value={selected.endpoint_path || ""} onChange={(v) => update("endpoint_path", v)} />
                <Select label="请求方式" value={selected.method || "POST"} onChange={(v) => update("method", v)} options={["POST"]} />
                <Select label="请求内容类型" value={selected.request_content_type || "multipart/form-data"} onChange={(v) => update("request_content_type", v)} options={["multipart/form-data", "application/json"]} />
                <Select label="认证方式" value={selected.auth_type || "bearer"} onChange={(v) => update("auth_type", v)} options={["bearer", "raw", "none"]} />
                <Input label="认证 Header 名称" value={selected.auth_header_name || ""} onChange={(v) => update("auth_header_name", v)} />
                <Input label="认证 Header 前缀" value={selected.auth_header_prefix || ""} onChange={(v) => update("auth_header_prefix", v)} />
                <Input label="图片字段名" value={selected.image_field_name || ""} onChange={(v) => update("image_field_name", v)} />
                <Input label="提示词字段名" value={selected.prompt_field_name || ""} onChange={(v) => update("prompt_field_name", v)} />
                <Input label="模型字段名" value={selected.model_field_name || ""} onChange={(v) => update("model_field_name", v)} />
                <Input label="输出张数字段名" value={selected.count_field_name || ""} onChange={(v) => update("count_field_name", v)} />
                <Input label="尺寸字段名" value={selected.size_field_name || ""} onChange={(v) => update("size_field_name", v)} />
                <Input label="质量字段名" value={selected.quality_field_name || ""} onChange={(v) => update("quality_field_name", v)} />
                <Select label="返回图片类型" value={selected.response_image_type || "base64"} onChange={(v) => update("response_image_type", v)} options={["base64", "url"]} />
                <Input label="返回图片字段路径" value={selected.response_image_path || ""} onChange={(v) => update("response_image_path", v)} />
                <Input label="超时时间" type="number" value={String(selected.timeout_seconds || 300)} onChange={(v) => update("timeout_seconds", Number(v || 300))} />
              </div>
              <label>额外参数 JSON</label>
              <textarea rows={5} value={selected.extra_params_json || "{}"} onChange={(event) => update("extra_params_json", event.target.value)} />
              <div className="check-row-group">
                <label className="check-row">
                  <input type="checkbox" checked={!!selected.enabled} onChange={(event) => update("enabled", event.target.checked)} />
                  是否启用
                </label>
                <label className="check-row">
                  <input type="checkbox" checked={!!selected.is_default} onChange={(event) => update("is_default", event.target.checked)} />
                  设为默认配置
                </label>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function Input({ label, value, onChange, type = "text", placeholder = "" }: { label: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type={type} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[] }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
