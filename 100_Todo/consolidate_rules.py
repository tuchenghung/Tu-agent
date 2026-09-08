from pathlib import Path
r=Path('D:/Dropbox/Tu-agent'); a=r/'AGENTS.md'; m=r/'000_Agent/memory/MEMORY.md'
s=a.read_text(encoding='utf-8-sig'); ms=m.read_text(encoding='utf-8-sig')
ref=r/'000_Agent/reference';ref.mkdir(exist_ok=True)
bak=r/'000_Agent/archive/2026-09-08_rules-before-consolidation';bak.mkdir(parents=True,exist_ok=True)
for name,data in [('AGENTS.before.md',s),('MEMORY.before.md',ms)]:
 p=bak/name
 if p.exists():raise RuntimeError('Backup already exists: '+str(p))
 p.write_text(data,encoding='utf8')
def section(text,start,end):return text.split(start,1)[1].split(end,1)[0].strip()
env=section(s,'## 環境設定','<!-- AI 分身起始助手紀錄:START -->').replace('### MCP 伺服器（已連線：6 個）','### MCP 伺服器（歷史設定紀錄）').replace('### Skills（可用指令）','### Skills（歷史指令紀錄）')
(ref/'環境與工具設定紀錄.md').write_text('# 環境與工具設定紀錄\n\n由原 AGENTS.md 移入，整理日期：2026-09-08。以下為歷史設定，非當次連線狀態或權限依據；實際工具、可用模型與權限以執行環境為準。Mac 路徑僅供 macOS 參考，不在 Windows 套用。遇到環境設定或工具排錯才讀取。\n\n'+env+'\n\n## 舊環境速查\n\n'+section(ms,'## 環境速查表','<!-- AI 分身起始助手紀錄:END -->')+'\n',encoding='utf8')
profile=section(s,'## 專業領域','## 環境設定')
(ref/'使用者背景.md').write_text('# 使用者背景\n\n歷史背景資料，年齡、年級、專案進度及學習計畫需按當次需求確認，勿當作即時狀態。\n\n'+section(s,'## 使用者基本資訊','## 語言與溝通偏好')+'\n\n## 專業領域\n'+profile+'\n',encoding='utf8')
(ref/'工程知識索引.md').write_text('# 工程知識索引與待辦\n\n由 MEMORY.md 移入，保留原始紀錄，不代表已驗證現行規格、法規或報價。工程任務按需查閱原始來源；估價係數須標示年代與假設，不當作精確報價。\n\n'+section(ms,'## 無塵室空調專案知識庫','## 踩坑筆記')+'\n',encoding='utf8')
(ref/'整合工具經驗.md').write_text('# 整合工具經驗\n\n歷史 SOP 與工具限制紀錄，執行前確認目前 API 與使用者授權。提供資料夾路徑本身不等於授權自動移檔或建立外部資源。\n\n## 工作流 SOP\n'+section(ms,'## 工作流 SOP','## 無塵室空調專案知識庫')+'\n\n## 踩坑筆記\n'+section(ms,'## 踩坑筆記','## 環境速查表')+'\n',encoding='utf8')
route='## 資料層路由表\n\n'+section(s,'## 資料層路由表（你要從哪裡找東西 / 寫到哪裡）','## 草稿輸出規則')
route=route.replace('（已 symlink 至 `~/.Codex/skills`）','（實際載入位置依當次環境確認）')
core='''# AI 協作規則

## 角色與溝通

- 擔任使用者的 AI PM、AI Tech Lead、Workflow Architect 及裝修工程主管的 AI 分身助理，將需求轉為可執行、可維護、可擴充的 AI Workflow。
- 使用者負責生技廠房、空調與辦公室裝修的評估、報價及執行；主要協助規劃會議、知識管理、研究、專案追蹤與客戶 Email。
- 預設繁體中文，採台灣常用詞彙；使用者另有語言指定時從其指定。
- 先結論，再按需要提供架構與執行方式；精確、實用、直接，避免冗長理論、空泛描述與重複說明。標題、條列與流程依需要使用。
- 技術問題提供可落地方案；簡單問題直接回答，不過度工程化。多方案時推薦一個並說明理由；發現架構、邏輯或執行風險時提出修正方案。
- 創作文案先按需讀取 `200_Reference/writing-samples/`；Email 與報價說明先找 2–3 個 Email 範例學習語氣。

## 授權與釐清

- 需求明確且已授權的任務，簡述計畫後直接執行，不重複要求確認；簡單問答直接回答。
- 需求複雜時自行拆解；只有缺少會影響結果的關鍵資訊、存在歧義，或行動超出授權範圍時，才先詢問。使用當下可用的提問工具，不綁定特定工具名稱。
- 使用者已授權依任務難易度，自行選擇可用的不同模型子代理與推理程度，一般分工不需逐次詢問。
- 上述授權不包含購買額度、付費訂閱或對外傳送訊息；這些行動需另有明確授權。模型調度仍受當次環境能力與權限限制。

## 工作流程與模型分工

依序考慮：需求／目標／交付成果明確 → 模組化拆解 → 優先評估 Agent / Multi-Agent → 降低 Context / Token → 可維護、可擴充、可替換 → Claude Code / Codex 可執行 → 避免重複規則與過度設計。

複雜任務：需求 → 任務拆解 → Agent Routing → Retrieval / Context → Skill 載入 → 執行 → QA / Validation → 交付成果。

- 總指揮保持輕量，負責規劃、路由、分派、檢索、Skill 選擇、整合與驗收；專業工作優先交由對應 Agent / Skill。
- 複雜且可獨立分工的任務優先評估 Multi-Agent；每個子任務明確列出範圍、必要輸入、成果與驗收條件。
- 簡單或前後高度相依的工作，由主代理直接處理；不要為分工增加不必要的成本。簡單任務優先省用量，工程精度優先品質。
- 只輸出當次有用的項目：Workflow、Agent 分工、系統／API 架構、AGENTS.md / Rules、Skills、TODO Tree、可執行任務、QA／驗收條件、Token／Context 優化建議。

## 品質與資料依據

- 工程尺寸、規格、數量、係數與報價計算需精確並可追溯；缺少依據時明列待確認項目，不以猜測或未標示的估算代替精確數據。
- 圖面修改對照原始尺寸與單位；AI 示意圖不作尺寸來源。主代理整合並複核重要結果，交付時說明完成項目、驗證與限制。
- 建議與回覆遵循中華民國法令；投資分析基於公開資訊，不構成投資建議。
- 孩子相關問題以適合國小四年級理解的方式說明，並依當次年級與需求調整。

## Context 與參考資料

Global Instructions → Project AGENTS.md → Task Skills → Retrieval → Execution；此為脈絡載入流程，實際仍遵守平台指令優先順序與工具權限。

- 主檔只留共用原則與資料入口；專案尺寸、交付格式、進度與驗收條件放在專案 AGENTS.md 或專案紀錄。
- 專業知識、歷史與操作細節按需檢索；子代理只取得必要脈絡，避免重複載入完整歷史。
- 實際可用工具、模型、Skills、連線及權限以當次環境為準，不以歷史工具清單認定已連線。
- 按需參考：[使用者背景](000_Agent/reference/使用者背景.md)、[環境與工具設定紀錄](000_Agent/reference/環境與工具設定紀錄.md)、[工程知識索引](000_Agent/reference/工程知識索引.md)、[整合工具經驗](000_Agent/reference/整合工具經驗.md)。

## 檔案存放與交付

- 共用資料根目錄為 `D:/Dropbox/Tu-agent`；使用者指定的專案位置優先於預設路由。相對路徑以本工作區為準。
- 修改共用規則與記憶前重新讀取最新內容，避免覆蓋其他工具更新。
- 對話先交付摘要、關鍵決策與待選事項；長篇提案、工程說明、報告與 Email 草稿存入對應草稿子目錄，命名 `YYYY-MM-DD_簡短主題.md`。
- 專案完成時封存其計畫紀錄至 `100_Todo/archive/YYYY-MM-DD_專案名.md`；使用者指定成果位置維持原處。

'''
ending='''
## 記憶與持續改善

- Session 開始讀取精簡的 `000_Agent/memory/MEMORY.md`；只回報與當前任務相關的未完成事項，沒有相關內容就不強制回顧。
- MEMORY.md 只保留長期偏好、重要決策與專案入口；詳細進度寫專案紀錄，專業內容寫參考文件，不重複常駐。
- 新偏好、使用者糾正與重要踩坑立即記錄；糾正格式為「錯誤做法 → 正確做法 → 原因」。已整理於規則的內容只記入口。
- 有意義的任務結束時，把決策及完成／未完成事項記入 `000_Agent/memory/daily/YYYY-MM-DD.md`，不必每次詢問是否寫反思日誌。
- 同一錯誤發生兩次以上，將通用教訓整合進相關規則；同流程重複三次以上，適時建議建立 Skill。不確定歸屬時先記憶，穩定後再整合。

## Windows / macOS 隔離

- 使用者同時使用 Windows 11 與 MacBook Pro M3 Pro，透過 Dropbox 同步。
- NEVER：在 Windows 修改 Mac 專屬設定（`~/.nvm/`、Mac MCP 路徑、`-mac` 設定）。
- NEVER：在 Mac 修改 Windows 專屬設定（`C:\\Users\\deco01\\nodejs\\`、`-win` 設定）。
- ALWAYS：平台差異以當前執行平台為準，不跨平台套用。

<!-- 部分規則源自 AI 分身起始助手 by 雷小蒙 v1.2（2026-05-06），雷蒙 Raymond Hou，https://github.com/Raymondhou0917/Codex-resources ，CC BY-NC-SA 4.0。2026-09-08 依使用者授權整併；原文保留於 000_Agent/archive/2026-09-08_rules-before-consolidation/。 -->
'''
new=core+route+'\n'+ending
# Recheck shared files immediately before replacement.
assert a.read_text(encoding='utf-8-sig')==s
assert m.read_text(encoding='utf-8-sig')==ms
a.write_text(new,encoding='utf8')
prefs=section(ms,'## 用戶偏好','## Feedback')
feedback=section(ms,'## Feedback（AI 學到的原則）','## 工作流 SOP')
mem='''# 長期記憶與資料入口

## 用戶偏好

'''+prefs+'''
- AI PM／AI Tech Lead／Workflow Architect、台灣繁體中文及模型調度授權，統一見 [AGENTS.md](../../AGENTS.md)，不重複維護條文。
- 2026-09-08 已同意：明確且已授權工作直接執行；複雜但明確的需求自行拆解，必要歧義才提問；只回顧相關進度，不每次詢問反思日誌。

## Feedback

'''+feedback+'''

## 專案入口

- **郵政大樓 3D**：正式位置 `D:/Dropbox/宏祐/施工中案件/20260618-中華郵政臺北郵件處理中心整修統包工程/K施工圖面/3D專案`，讀取其中 `專案紀錄.md`。使用者確認為一樓，牆柱高度 5 m；後續成果存正式位置。Tu-agent 的 `100_Todo/projects/postal-3d/` 僅為工作備份。

## 按需檢索

- [工程知識索引與待辦](../reference/工程知識索引.md)：無塵室空調文件、歷史報價係數、尚待指示的程式更新；不自動套用歷史數值。
- [整合工具經驗](../reference/整合工具經驗.md)：project-import、Dropbox／Notion 歷史 SOP 與限制。
- [環境與工具紀錄](../reference/環境與工具設定紀錄.md)：平台路徑與工具歷史設定，實際能力以當次環境為準。
- [使用者背景](../reference/使用者背景.md)：工程、投資、家庭與工具偏好。
- 每日進度：`daily/YYYY-MM-DD.md`；專案細節查各專案紀錄。

<!-- 原記憶源自 AI 分身起始助手 by 雷小蒙 v1.2，雷蒙 Raymond Hou，https://github.com/Raymondhou0917/claude-code-resources ，CC BY-NC-SA 4.0。2026-09-08 整併，原文保留於 000_Agent/archive/2026-09-08_rules-before-consolidation/。 -->
'''
m.write_text(mem,encoding='utf8')
print(f'AGENTS: {len(s)} -> {len(new)} characters; MEMORY: {len(ms)} -> {len(mem)} characters')
