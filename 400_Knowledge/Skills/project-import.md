# project-import｜工程專案資料夾匯入

> 建立日期：2026-05
> 狀態：✅ 運作中

## 是什麼
把 Dropbox 工程專案資料夾自動掃描、分類，並在 Notion 建立對應專案頁面的 Command。
觸發方式：提供 Dropbox 專案資料夾路徑。

## 為什麼做
每個工程案子收到的資料散落各處（平面圖、報價、合約、照片），需要統一整理進 Notion。

## 怎麼運作
1. 掃描資料夾內容
2. 依 A-I 分類移檔
3. 在 Notion Projects DB 建立專案頁面
4. 建立折疊標題（heading_2 toggleable）

## 關聯資料
- Command 檔：`.claude/commands/project-import.md`
- Notion Projects DB：`3355cac1-0351-4ef4-8eb1-8b8f0bb619c3`

## 踩坑紀錄
- `heading_2 toggleable` 需用 Node.js 直接呼叫 Notion API，MCP 工具不支援
- 實際驗證案例：羅東聖母醫院S棟5樓（2026-05-15）、南投基督教醫院（2026-05-15）
