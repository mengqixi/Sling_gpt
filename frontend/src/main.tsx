import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { History, KeyRound, LayoutDashboard, Palette, Wand2 } from "lucide-react";
import Generate from "./pages/Generate";
import RecolorPage from "./pages/Recolor";
import PromptTemplates from "./pages/PromptTemplates";
import ApiConfigs from "./pages/ApiConfigs";
import HistoryPage from "./pages/History";
import "./styles.css";

type Page = "recolor" | "generate" | "prompts" | "api" | "history";

function App() {
  const [page, setPage] = useState<Page>("recolor");
  const [generateSources, setGenerateSources] = useState<any[]>([]);
  const nav = [
    { key: "recolor" as Page, label: "智能调色", icon: Palette },
    { key: "generate" as Page, label: "AI 生成", icon: Wand2 },
    { key: "prompts" as Page, label: "提示词管理", icon: LayoutDashboard },
    { key: "api" as Page, label: "API 设置", icon: KeyRound },
    { key: "history" as Page, label: "历史记录", icon: History }
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">B</div>
          <div>
            <strong>女包 AI 生图工具</strong>
            <span>内部设计工作台</span>
          </div>
        </div>
        <nav>
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.key} className={page === item.key ? "active" : ""} onClick={() => setPage(item.key)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
      <main>
        {page === "recolor" && (
          <RecolorPage
            onUseAsSource={(image) => {
              setGenerateSources([image]);
              setPage("generate");
            }}
          />
        )}
        {page === "generate" && <Generate initialUploadedImages={generateSources} />}
        {page === "prompts" && <PromptTemplates />}
        {page === "api" && <ApiConfigs />}
        {page === "history" && <HistoryPage />}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
