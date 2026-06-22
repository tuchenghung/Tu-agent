---
name: 工法入庫
description: "建材/工法/廠商資料入庫 — 同步建立裝修百科全書條目、供應商記錄、本機知識庫，並在兩者間建立 Notion 頁面超連結。輸入 /工法入庫 觸發，或貼上產品/工法/廠商資料時主動詢問是否入庫。"
---

# 工法入庫 SOP

## 觸發條件
- 使用者輸入 `/工法入庫`
- 使用者貼上產品規格、工法說明、廠商資料 → 判斷屬建材/工法類 → 主動詢問「要入庫嗎？」

---

## 資料庫常數（勿改動）
- **裝修百科全書** DB ID：`1e25b3e6-e630-4f67-8677-f97a9a8dd159`
- **供應商資料庫** DB ID：`8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b`
- **本機路徑（Mac）**：`/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/400_Knowledge/工程/建材規格/`
- **本機路徑（Win）**：`D:\Dropbox\Tu-agent\400_Knowledge\工程\建材規格\`
- **Notion Token**：`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`

---

## Step 1：確認入庫資料

從使用者提供的內容中提取以下欄位（不足則主動詢問）：

| 欄位 | 必填 | 說明 |
|------|------|------|
| 產品/工法名稱 | ✅ | 主標題 |
| **來源（必填）** | ✅ | **網址 / 本機檔案路徑 / 報告編號 / 廠商提供文件名稱，缺少來源不得入庫** |
| 規格數據 | ✅ | 尺寸、係數、型號、測試標準等 |
| 適用場景 | ✅ | 哪些情境適合 |
| 不適用場景 | ✅ | 哪些情境不適合（很重要） |
| 施工注意事項 | ⬜ | 有就填 |
| 分類 | ✅ | 從以下選一：機電/空調/水電/泥作/木作/油漆/裝修/消防/其他/法規/設備 |
| 供應商公司名 | ✅ | 一家或多家 |
| 供應商電話 | ⬜ | |
| 供應商地址 | ⬜ | |
| 供應商 Email | ⬜ | |
| 供應商網址 | ⬜ | |

整理好後向使用者摘要確認，再繼續執行。

---

## Step 2：建立裝修百科全書條目

用 `mcp__notion__API-post-page` 建立：

```
parent: {"database_id": "1e25b3e6-e630-4f67-8677-f97a9a8dd159"}
properties:
  標題: 產品/工法名稱
  分類: 對應選項
  主管機關/來源: 廠商名稱（多家用 / 分隔）
  摘要: 一段話摘要（含NRC/STC/規格重點 + 適用/不適用場景）
```

**記錄回傳的 `page_id` 和 `url`（後續步驟需要）**

---

## Step 3：建立或確認供應商條目

對每一家供應商：

1. 先用 `mcp__notion__API-post-search` 搜尋公司名
2. 若已存在 → 記錄現有 `page_id` 和 `url`，不重複建立，在備註加上新產品資訊
3. 若不存在 → 用 `mcp__notion__API-post-page` 建立：

```
parent: {"database_id": "8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b"}
properties:
  供應商名稱: 公司名
  電話: 電話
  手機: 辦公室電話（若有）
  地址: 地址
  電子郵件: email
  網址: 網址
  工種類別: 對應工種（建材料供應/空調工程/etc）
  合作狀態: 評估中
  備註: 產品描述 + 來源說明
```

**記錄所有供應商的 `page_id` 和 `url`**

---

## Step 4：建立雙向頁面連結

用以下 Python 腳本透過 Notion REST API 在兩個頁面的 body 加入連結（MCP 工具不支援此操作）：

```python
import json, urllib.request

TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def append_blocks(page_id, blocks):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    body = json.dumps({"children": blocks}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="PATCH")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def text_block(content, bold=False):
    return {"type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": content},
         "annotations": {"bold": bold}}
    ]}}

def link_block(label, url):
    return {"type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": "→ " + label, "link": {"url": url}}}
    ]}}

# 在裝修百科頁面加入「提出廠商」區塊
append_blocks(百科_page_id, [
    {"type": "heading_3", "heading_3": {"rich_text": [{"type":"text","text":{"content":"🏢 提出廠商"}}]}},
    link_block(供應商名稱, 供應商_notion_url),
])

# 在供應商頁面加入「相關工法/建材」區塊
append_blocks(供應商_page_id, [
    {"type": "heading_3", "heading_3": {"rich_text": [{"type":"text","text":{"content":"📚 相關工法/建材"}}]}},
    link_block(產品名稱, 百科_notion_url),
])
```

若有多家供應商，在百科頁面列出所有供應商連結；在每家供應商頁面各自加入百科連結。

---

## Step 5：本機知識庫

建立 markdown 檔案：
- 路徑（Mac）：`/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/400_Knowledge/工程/建材規格/YYYY-MM-DD_產品名.md`
- 路徑（Win）：`D:\Dropbox\Tu-agent\400_Knowledge\工程\建材規格\YYYY-MM-DD_產品名.md`
- 日期：今天的日期（從 MEMORY.md currentDate 讀取）

檔案內容包含：
```markdown
---
tags: [工法, {工種}, {關鍵字1}, {關鍵字2}]
date: YYYY-MM-DD
category: {工種工程}
來源: {路徑或網址}
---

# 產品名（品牌）

## 產品資訊
- 品牌、型號、材質、厚度、尺寸、認證

## 關鍵數據
| 項目 | 數值 |
|------|------|
| 數據名 | 數值 + 單位 |

## 選用判斷
| 需求 | 適合？ |
|------|--------|
| 場景 | ✅/⚠️/❌ |

> [!warning] 施工禁令
> - 列出絕對禁止事項（化學相容、材料規格、操作限制等）

> [!tip] 施工要點
> - 列出關鍵施工步驟與品質控制要點

> [!info] 驗收稽核清單
> - 列出驗收時需核對的項目

## 供應商
| 公司 | 電話 | 網址 |
|------|------|------|

## Notion 連結
- 裝修百科：[URL]
- 供應商：[URL]

---

## 工種分類

[[對應工種名]]
```

**工種 hub 對應表（依 Step 1 分類自動選）：**

| 分類 | 工種 hub |
|------|---------|
| 空調 | [[空調工程]] |
| 機電 / 水電 | [[機電工程]] |
| 消防 | [[消防工程]] |
| 泥作 | [[泥作工程]] |
| 木作 | [[木作工程]] |
| 地板 | [[地板工程]] |
| 鋁窗 / 鐵窗 | [[鋁窗鐵窗工程]] |
| 吸音 / 隔音 | [[吸音隔音工程]] |
| 裝修（其他）| 依實際內容選最近的工種 |

**同時更新對應 hub 頁：**
在 `400_Knowledge/工程/{工種}.md` 的「建材規格知識庫」區段末尾加一行：
`- [[YYYY-MM-DD_產品名]]`

---

## Step 6：確認輸出

完成後向使用者回報：

```
✅ 裝修百科全書：[頁面名稱](Notion URL)
✅ 供應商（新建）：[公司名](Notion URL)
  or
✅ 供應商（已存在）：[公司名](Notion URL) — 已補充產品資訊
✅ 本機：400_Knowledge/工程/建材規格/YYYY-MM-DD_產品名.md
```

---

## Step 7：更新記憶

在以下路徑追加這筆入庫記錄（依執行平台選擇）：
- Mac：`/Users/tuzhenghong/.claude/projects/-Users-tuzhenghong-Library-CloudStorage-Dropbox-Tu-agent/memory/ref_建材工法庫.md`
- Win：`C:\Users\deco01\.claude\projects\D--Dropbox-Tu-agent\memory\ref_建材工法庫.md`

格式：
```
- YYYY-MM-DD｜產品名｜分類｜廠商名｜[百科連結](URL)
```

若檔案不存在則新建，並在 MEMORY.md 加上索引行。

---

## 未來對話主動提醒規則

當使用者詢問以下主題時，**先 Grep `400_Knowledge/工程/建材規格/`** 找相關檔案：
- 隔音、吸音、噪音、回音、殘響
- 建材、工法、裝修、施工
- 其他曾入庫的產品類別

若找到相關資料 → 在回答前或回答後提醒：
> 「📚 建材規格庫有 [產品名] 的完整資料，需要我調出來嗎？」


---

## 分類

[[Skill目錄]]
