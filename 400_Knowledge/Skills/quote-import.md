# quote-import｜報價單匯入 Notion

> 建立日期：2026-04
> 狀態：✅ 運作中

## 是什麼
把 PDF / Excel / JPG 報價單自動匯入 Notion 的 Skill。
觸發方式：`/quote-import` 或提供報價單檔案路徑。

## 為什麼做
工程報價單格式雜亂（PDF/Excel/手寫掃描），手動輸入 Notion 耗時且容易出錯。

## 怎麼運作
1. 讀取報價單檔案
2. 建立摘要讓用戶確認
3. 查詢或建立供應商頁面
4. 建立工程報價品項
5. 建立工作文件中心報價單文件
6. 填寫所有 Notion 關聯與欄位

## 關聯資料
- Skill 檔：`000_Agent/skills/quote-import/`
- 另有繁體版：`000_Agent/skills/報價單輸入資料庫/`

## 踩坑紀錄
- Notion MCP 無法建立 `heading_2 toggleable`，需改用 Node.js 直接呼叫 Notion REST API
