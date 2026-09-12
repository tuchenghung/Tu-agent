# Todoist 共用任務通道

更新：2026-09-11（Claude Code Windows 完成驗證＋補齊三專案）

## 目前狀態
- Claude Code（Windows，本專案 `.mcp.json` http 入口）已完成Todoist OAuth並可用 `mcp__todoist__find-projects`／`add-projects` 實際操作，非Codex外掛。此段取代前文「不能宣稱MCP已可操作」。
- 三分類專案已查重補齊，實際ID如下（皆為Free版個人專案，非workspace）：
  - 宏祐：`6hVJw9Jxq5jMCqwg`（沿用先前網頁建立的專案，未重複新增）
  - YUSHI：`6hVM35q4qp5hpQJw`（2026-09-11新建；命名採YUSHI而非本檔案先前寫的YASHI，統一對齊Notion／記帳／報價單既有拼法，避免同一廠商跨系統出現兩種名稱）
  - 個人待辦：`6hVM35mfgfF9Pvhq`（2026-09-11新建）
- 三專案建立後已用 `find-projects` 重讀核對，確認名稱與ID正確；未建立任何測試任務、未設定到期日。
- Todoist先用免費版；不啟用付費或Pro試用。

## Claude Code 接續
- Codex外掛授權不等於Claude Code已授權。Claude須先檢查實際工具／MCP，能列出Todoist專案才算可用。
- 官方共用服務入口：https://ai.todoist.net/mcp（HTTP）。兩個工具各自授權同一個Todoist帳號，不複製登入憑證，不將token寫進Dropbox。
- 若Claude尚未設定，可依官方文件執行：claude mcp add --transport http todoist --scope user https://ai.todoist.net/mcp
- 先查現有設定，避免重複；使用者在Claude Code的/mcp完成OAuth授權。Windows與Mac分別設定，不跨平台改設定。本次未修改Claude設定或完成其授權。
- 官方依據：https://developer.todoist.com/api/v1/#tag/Todoist-MCP 、https://code.claude.com/docs/en/mcp

## 共用TASK規則
- 優先Todoist MCP／API，只有登入或不支援功能才使用網頁介面。
- Todoist主控待辦日期與完成狀態；Google Calendar放時段預約；Notion保存案件資料，初期以案件頁連結串接，不自動雙向回寫。
- 分類：宏祐、YUSHI（原誤寫YASHI，2026-09-11由Claude Code建立時對齊系統既有拼法）、個人待辦；建立前列出現有專案並記錄實際ID。任務使用「案件名｜具體動作」，描述附已核實Notion案件連結。
- 新增前查同案同事項，既有任務優先更新；不同集團不得因同名混用。沒有明確日期不臆造到期日。
- 完成寫入後重讀，回報任務ID／連結與日期；未知結果先查核，不直接重送。

## 接續驗證
1. ~~在能載入外掛的新工作階段列出Todoist專案，確認正確帳號。~~ 2026-09-11 Claude Code（Windows）已完成，見上方「目前狀態」三個實際ID。
2. ~~補齊三類專案，先查重。~~ 2026-09-11 Claude Code完成：宏祐（沿用既有）＋新建YUSHI、個人待辦，皆已重讀核對。
3. 經使用者指定時間建立提醒測試，由手機確認通知；不以API成功代替手機驗收。（尚未執行——本次刻意不建測試任務、不設到期日）
4. ~~Claude Code完成獨立授權後讀到同一批專案，才標記雙入口可用。~~ 2026-09-11已完成：Claude Code（Windows）可讀寫，Codex外掛端是否同步讀到同一批專案待Codex工作階段自行驗證。

## 本次錯誤紀錄
- 誤用Apple Music外掛ID → 安裝前逐字核對外掛名稱與ID → 避免無關服務授權。錯誤請求已停止，工具回傳未確認、未完成安裝。

## 接續：Claude Code共用設定已建立
- 已先查本專案與使用者設定未見Todoist入口，再透過Claude官方CLI建立D:/Dropbox/Tu-agent/.mcp.json，todoist使用http與https://ai.todoist.net/mcp；已重讀核對。
- 本設定僅公開服務位址，無token，可作此Dropbox專案共用入口；未修改Mac專屬設定或使用者其他MCP。
- Claude Code在此專案載入後，透過/mcp核准專案伺服器並完成Todoist OAuth；不再另加user scope重複設定。此段取代前文「本次未修改Claude設定」。
- 尚未OAuth或成功列出專案，不能宣稱Claude已可建立TASK。Codex當前工具清單仍無Todoist工具，需在載入外掛的工作階段驗證。

## 最新：Claude Code已寫回專案ID及驗證結果
- 2026-09-11 Claude Code（Windows，本專案`.mcp.json` http入口）用`mcp__todoist__find-projects`確認帳號與既有專案（Inbox／Getting Started／宏祐`6hVJw9Jxq5jMCqwg`），查重後用`add-projects`新建YUSHI`6hVM35q4qp5hpQJw`與個人待辦`6hVM35mfgfF9Pvhq`，再重讀`find-projects`核對五個active專案名稱與ID皆正確。此段補齊前段「除宏祐既有網址外其餘ID待補齊」的缺口。
- 命名以YUSHI取代本檔案先前的YASHI（經使用者確認選YUSHI，理由：對齊Notion／記帳／報價單既有拼法）。
- 依指示未建立任何測試任務、未設定到期日，僅完成專案層級的查重與補齊。
- Codex本工作階段尚未取得Todoist工具；手機提醒、Google Calendar與Notion自動同步均未驗證，不能把專案建立完成當成全部連動完成。

## Codex官方MCP連線接續
- 使用者反映手機看不到專案並要求Codex直接連接。實查codex mcp get todoist原先不存在；現已新增官方HTTP MCP至Windows Codex，OAuth等待使用者授權，尚未完成讀取驗證。
- 本次重新讀到Claude已補寫三類專案ID，且使用者在Claude選用YUSHI名稱；以該最新段落為準，不再建立YASHI重複專案。手機看不到的原因仍待同帳號／同步核對，不猜測。

- OAuth最新結果：Codex登入流程已回傳Successfully logged in，授權成功，取代上一段等待授權。當前對話工具尚待重新載入；未直接讀取帳號與專案。

## 最新驗證：Codex 雙入口讀取成功（2026-09-11 16:46 台北時間）
- 本次透過 Todoist 外掛與官方 mcp__todoist 入口各自呼叫 user_info／find_projects，均確認同一帳號：阿宏，gemini7361@gmail.com，userId 60684655，Asia/Taipei，Todoist Free。取代上文 Codex 尚無工具或未讀取驗證的舊狀態。
- 兩入口均列出五個專案且無下一頁；宏祐 6hVJw9Jxq5jMCqwg、YUSHI 6hVM35q4qp5hpQJw、個人待辦 6hVM35mfgfF9Pvhq 與 Claude 紀錄完全一致，皆未封存、未加入最愛、個人非共享專案，無 workspaceId。未新增或修改任何 Todoist 專案及任務。
- 2026-09-11 今天含逾期未完成任務為 0；全帳號未完成任務 17 筆，皆為 Getting Started 教學任務，三個自訂專案目前各 0 筆未完成任務。user_info 回報今天已完成 3 筆。
- 今天頁面空白符合目前任務資料；若手機在專案清單也看不到三個專案，仍需使用者提供手機帳號 Email 與所在頁面才能區分帳號差異、檢視位置或同步問題，尚不能宣稱已確診或修復。已向使用者提出此核對問題。
- 官方排查依據：https://www.todoist.com/help/todoist/troubleshooting/troubleshoot-syncing-issues-in-todoist-d6dDzzpF 。手機提醒尚未驗收。

## 手機顯示確認（2026-09-11）
- 使用者回覆「我有看到項目了」，確認手機已可看到專案，專案顯示問題結案；沿用既有三個專案，不重複建立。
- 先前未顯示的具體原因未確認，不歸因於帳號錯誤或同步故障。此確認僅涵蓋專案可見，手機提醒通知仍未驗收。

## 手機提醒測試已設定（2026-09-11）
- 使用者指定「現在」測試，查重後在個人待辦建立「Todoist 手機提醒測試」，taskId：6hVM5xrCqJvWhG4q，日期時間：2026-09-11 16:51（Asia/Taipei）。
- 沿用系統自動建立的到期提醒 6hVM5xpq7rjvjvRH，明確更新 service=push、minuteOffset=0，避免重複提醒；任務與提醒均已重讀核對。未付費或啟用試用。
- 手機實際收到通知仍待使用者回覆，不以 MCP 設定成功代替手機驗收。

## 手機推播驗收完成（2026-09-11）
- 使用者回覆「收到」，確認 16:51 的 Todoist 手機提醒測試推播實際送達，取代前段尚待手機驗收狀態。
- 測試任務 6hVM5xrCqJvWhG4q 已由 MCP 標記完成，工具回傳成功。三個既有專案維持原狀。
- Todoist 帳號／三專案讀取、手機專案可見及本次手機推播測試皆已完成驗證；Google Calendar／Notion 自動同步不在本次驗收範圍。

## Todoist 接續流程糾正（2026-09-11）
- 錯誤做法：手機提醒測試完成後，要求使用者從頭提供第一筆待辦。
- 正確做法：先檢索既有 Todoist、專案與工作紀錄，排除已完成及重複事項，整理目前需追蹤的 TASK，再處理缺少的日期／提醒時間。
- 原因：使用者預期助理主動找出既有工作，不把可檢索資訊轉嫁給使用者重述。未核實期限不臆造日期，舊付款紀錄不直接當成現在欠款。
- 本次已重查 Todoist 全部未完成任務（17筆教學任務，無正式工作任務）及本機專案紀錄；候選清單見 100_Todo/drafts/2026-09-11_現有待辦與提醒候選.md。尚未設定正式提醒，亦未查核 Notion 線上案件／帳款最新狀態。

## 新增任務 Skill 已切換 Todoist（2026-09-11）
- 錯誤：只更新通道／記憶，Claude /新增任務仍讀到舊 Notion＋Calendar 流程 → 修正：更新 000_Agent/skills/新增任務/SKILL.md 為唯一共用規則，.claude/commands/新增任務.md 改為引用入口，新增 .claude/skills/todoist-tasks/SKILL.md 提供自然語句探索 → 原因：讓 Claude 與 Codex 共用同一流程，避免副本漂移。
- 已涵蓋帳號／三專案查重、先找現有TASK、依授權新增更新、無日期不臆造、push提醒查重與回讀、手機驗收及完成；移除必問優先級與自動Calendar事件。
- 已回讀兩入口並核對相對路徑存在，檢查規則與本次實測一致。官方 quick_validate 因本機缺 PyYAML 未執行成功；未實際啟動新Claude會話驗證自動探索。現有Claude會話可直接讀取共用檔或執行 /新增任務。
- 現有待辦候選清單仍待正式任務／提醒排程，使用者最新要求先完成Skill更新並回報。

## Google日曆最新決議與收尾（2026-09-11）
- 使用者同意有日期時間的Todoist任務透過原生日曆整合顯示Google Calendar，避免人工複製事件或雙重通知。無日期任務留Todoist，全天任務同步尚未指定。
- 已查官方說明並開啟設定頁，但僅見載入狀態，尚未確認Google帳號／連線、啟用同步或驗證事件；不得宣稱已整合。
- 共用新增任務Skill已記此最新決策與未完成狀態；下次先核對原生整合，再處理6項候選任務。今日完整收尾見 ../memory/daily/2026-09-11.md。
- 官方依據：https://www.todoist.com/help/todoist/integrations/use-the-calendar-integration-rCqwLCt3G
