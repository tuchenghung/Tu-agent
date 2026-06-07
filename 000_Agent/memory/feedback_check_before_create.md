---
name: feedback-check-before-create
description: 建立 Notion 資料庫或頁面前必須先確認是否已存在，避免重複建立
metadata:
  type: feedback
---

建立任何 Notion 資源（database、page、inline database）前，必須先查該頁面是否已有相同名稱的資源存在。

**Why:** 曾在專案管理頁面建出兩個「業主收款記錄」資料庫（差 1 分鐘），空白的那個造成混亂，需要事後手動刪除。

**How to apply:**
- 用 `API-get-block-children` 列出目標頁面的所有 block，確認無同名資料庫後再建立
- 建收款紀錄、發包明細等子資料庫時同樣適用
- 搜尋到已有同名資源 → 直接用現有的，不重建
