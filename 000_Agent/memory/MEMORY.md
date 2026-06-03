<!-- AI 分身起始助手紀錄:START -->
<!-- AI 分身起始助手 by 雷小蒙 v1.2 · 2026-05-06 · by 雷蒙（Raymond Hou）· https://github.com/Raymondhou0917/claude-code-resources · CC BY-NC-SA 4.0 -->

# 裝修工程接案主管的 AI 分身記憶

> 這裡存我跟 AI 之間跨 session 的偏好、經驗、踩坑紀錄。
> AI 每次 session 開始會自動讀這個檔案。

---

## 用戶偏好

（還是空的，等你跟 AI 合作幾次後自然會長出來）

---

## Feedback（AI 學到的原則）

- **雙系統隔離原則**：使用者同時有 Windows 11（PC）與 macOS（MacBook Pro M3 Pro），兩邊透過 Dropbox 同步專案資料夾。在 Windows 操作時不得修改 Mac 專屬設定（如 `~/.nvm/`、Mac 路徑的 MCP 設定）；在 Mac 操作時同理不動 Windows 設定（如 `C:\Users\deco01\nodejs\`、`-win` 結尾的 MCP 設定）。設定檔若有平台差異，以當前執行平台為準，不要跨平台套用。

---

## 工作流 SOP

### /project-import — 工程專案資料夾匯入
- **觸發**：使用者提供 Dropbox 專案資料夾路徑
- **功能**：自動掃描 → 依 A-I 分類移檔 → 建 Notion 專案頁面 → 建折疊標題
- **Skill 檔**：`.claude/commands/project-import.md`
- **關鍵**：heading_2 toggleable 需用 Node.js 直接呼叫 Notion API（MCP 工具不支援）
- **Notion Projects DB**：`3355cac1-0351-4ef4-8eb1-8b8f0bb619c3`
- **實際驗證案例**：羅東聖母醫院S棟5樓耳鼻喉科（2026-05-15）、南投基督教醫院（2026-05-15）

---

## Dropbox API

| 項目 | 值 |
|---|---|
| 申請頁面 | https://www.dropbox.com/developers/apps |
| Token 有效期 | 約 4 小時，需手動重新產生 |
| Token 位置 | Settings → OAuth 2 → Generate access token |
| 必要 Permission | `sharing.write`（在 Permissions 頁籤勾選）|
| 建立/取得分享連結腳本 | `D:\Dropbox\Tu-agent\000_Agent\scripts\dropbox_notion_links.mjs` |

---

## 無塵室空調專案知識庫（2026-06-03 建立）

參考資料路徑：`400_Knowledge/工程/建材規格/`

| 知識文件 | 重點內容 |
|---------|---------|
| `2026-06-03_MAU外氣處理機規格與報價參考.md` | 弘振/勝新 MAU 報價（2010，矽品）；元/CMM 分析；組裝費 |
| `2026-06-03_AHU空調箱規格與報價參考.md` | 弘振 AHU 全機型（1400~80CMM），元/CMM 分析，2011年未稅 |
| `2026-06-03_水冷式冰水主機規格與報價參考.md` | 日立 RCU-409WS，28RT/30kW，467,800/台含稅（2011） |
| `2026-06-03_氣冷分離式冷氣機規格與報價參考.md` | 大同 TFP 系列完整規格，8RT=90,000/組含稅（2011） |
| `2026-06-03_空調箱濾網規格與報價參考.md` | 晨鼎/AIRREX；初效 75/只，袋型 770/只（2011） |
| `2026-06-03_起重設備安裝定位費用參考.md` | AHU 16,000/台，全廠一批 19~22萬含稅（2011） |
| `2026-06-03_冷氣單位換算表.md` | 1RT=2,500kcal=10,000BTU≈2.9kW，台灣慣用值 |
| `2026-06-03_三相380V馬達電力配線規格表.md` | CNS-2934 vs Appendix D FLA 對比；EMT 選型；法規214/220條 |
| `2026-06-03_無塵室空調監控系統IO點數表.md` | SP-IC-FO01 DXF 解析；118點；每台MAU=22點；DDC架構 |
| `2026-06-03_無塵室空調控制架構圖說參考.md` | STAND-ALONE DDC；MAU/乾盤/FFU/排氣控制點位圖 |
| `2026-06-03_空調配管施工規範重點.md` | 管材/保溫厚度/水壓試驗/吊架間距/冰水主機R-134a規格 |

**程式待更新（等「更新」指令）**：
- FLA 表：從 Appendix D 改為 CNS-2934（法規依據）
- 導線截面積：從 FLA 直接查表改為 FLA×1.25（法規第214條）
- EMT 選管：改為填充率計算（40%填充，實際管內徑）
- MAU 單價：275,000/台 → 依 CMM 分級計算
- 乾盤單價：45,000/台 → 35,000/台（2025年估）

---

## 踩坑筆記

- `mcp__notion-win__API-patch-block-children` 只支援 `paragraph` / `bulleted_list_item`，無法建立 `heading_2 toggleable`。需用 Node.js + Notion REST API 直接建立。

---

## 環境速查表

| 項目             | 值                                             |
| :--------------- | :--------------------------------------------- |
| AI 分身母資料夾  | `/Users/tuzhenghong/Tu-agent`（symlink → `~/Dropbox/Tu-agent`） |
| 建立日期         | `2026-04-30`                                   |
| Skills symlink   | ✅ `~/.claude/skills` → `000_Agent/skills/`    |
| 記憶系統啟用     | ✅                                             |
| 日記功能         | ✅ `300_Journal/` 已建立                       |

<!-- AI 分身起始助手紀錄:END -->
