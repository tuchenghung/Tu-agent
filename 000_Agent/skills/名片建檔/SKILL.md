---
name: 名片建檔
description: "名片建檔 Skill — 收到名片照片後，自動辨識聯絡資料 → 確認摘要 → 查重 → 建立 Notion 名片資料庫記錄 → 複製照片到 Dropbox → 取得分享連結 → 更新 Notion 名片檔案欄位。觸發方式：使用者提供名片照片，或直接輸入 /名片建檔。"
---

# 名片建檔 SOP

## 資料庫 ID（固定，勿更改）

| 資料庫 | ID |
|--------|-----|
| 名片資料庫 | `3e062638-1e7c-4a54-bb0a-012bdbbb64c8` |

## Dropbox 名片歸檔路徑

```
/Tu-agent/400_Knowledge/工程/客戶/名片/
```
本機對應路徑（Mac）：
```
/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/400_Knowledge/工程/客戶/名片/
```

---

## 執行步驟

### STEP 1：辨識名片資訊

使用 `Read` 工具讀取使用者提供的圖片（JPG / PNG / PDF），辨識以下欄位：

| 欄位 | Notion 屬性 | 說明 |
|------|------------|------|
| 姓名 | `姓名`（title） | 聯絡人全名 |
| 公司/單位 | `公司/單位` | 服務公司或單位名稱 |
| 職稱 | `職稱` | 如：董事長、業務、專案經理 |
| 手機 | `手機` | 行動電話 |
| 公司電話 | `公司電話` | 辦公室電話（含分機） |
| Email | `Email` | 電子郵件 |
| 地址 | `地址` | 公司地址 |
| 統一編號 | `統一編號` | 8碼統編 |
| LINE ID | `LINE ID` | 若有 |
| 備註 | `備註` | 其他資訊（如：資格證照、公司資格登記別） |

整理後以表格呈現，詢問使用者：「以上資訊是否正確？是否繼續建立？」

**等待使用者確認後才繼續，若有修正先更新再進行下一步。**

---

### STEP 2：判斷分類與工種

根據名片資訊自動判斷：

**分類（`分類` select）：**

| 判斷條件 | 分類值 |
|---------|--------|
| 業主、院方、機關單位 | 業主/客戶 |
| 建築師事務所 | 建築師 |
| 室內設計公司 | 室內設計 |
| 機電技師 | 機電技師 |
| 消防設備師 | 消防設備師 |
| 結構技師 | 結構技師 |
| 營造廠、統包商 | 營造/統包 |
| 協力廠商（空調/水電/木作等施工廠） | 協力廠商 |
| 材料商、設備供應商 | 材料供應 |
| 主管機關 | 主管機關 |
| 其他 | 其他 |

**工種（`專長/工種` multi_select，可複選）：**

| 名片內容 | 工種選項 |
|---------|---------|
| 冷凍、空調、HVAC、冷氣 | 空調HVAC |
| 水電、電氣、配線 | 水電ELEC |
| 機電、MEP | 機電MEP |
| 消防、灑水 | 消防FIRE |
| 木作、裝修、室內裝潢 | 木作CARP |
| 油漆、塗裝 | 油漆PAINT |
| 鐵工、鋼構、金屬 | 金屬METAL |
| 玻璃、帷幕 | 玻璃GLASS |
| 地板、地磚、地坪 | 地坪FLOOR |
| 天花、輕鋼架 | 天花CEIL |
| 輕隔間、隔間 | 輕隔間PART |
| 指標、標示 | 指標SIGN |
| 清潔 | 清潔CLEAN |
| 搬運、傢俱 | 搬運/傢俱 |
| 設計、規劃 | 設計/規劃 |
| 審查、簽證 | 審查/簽證 |

服務區域（`服務區域` multi_select）從地址或名片描述判斷，預設填「台北」。

---

### STEP 3：查重

使用 `mcp__notion__API-post-search` 搜尋名片資料庫，確認是否已存在相同聯絡人。

搜尋條件：以「姓名」或「公司名稱」搜尋。

**情況 A：未找到重複** → 繼續 STEP 4

**情況 B：找到疑似重複**
1. 列出符合的記錄名稱與 Notion 連結
2. 詢問使用者：
   ```
   ⚠️ 名片資料庫已有相似記錄：
   - {姓名}（{公司}）{Notion連結}

   [ 是重複，取消 ] / [ 非重複，繼續建立 ] / [ 更新現有記錄 ]
   ```
3. **等待使用者確認後才繼續**

---

### STEP 4：建立 Notion 名片記錄

使用 `mcp__notion__API-post-page` 在名片資料庫建立：

```json
{
  "parent": { "type": "database_id", "database_id": "3e062638-1e7c-4a54-bb0a-012bdbbb64c8" },
  "icon": { "type": "emoji", "emoji": "🏢" },
  "properties": {
    "姓名": { "title": [{ "type": "text", "text": { "content": "{姓名}" } }] },
    "公司/單位": { "rich_text": [{ "type": "text", "text": { "content": "{公司}" } }] },
    "職稱": { "rich_text": [{ "type": "text", "text": { "content": "{職稱}" } }] },
    "手機": { "phone_number": "{手機}" },
    "公司電話": { "phone_number": "{公司電話}" },
    "Email": { "email": "{email}" },
    "地址": { "rich_text": [{ "type": "text", "text": { "content": "{地址}" } }] },
    "統一編號": { "rich_text": [{ "type": "text", "text": { "content": "{統編}" } }] },
    "LINE ID": { "rich_text": [{ "type": "text", "text": { "content": "{LINE}" } }] },
    "分類": { "select": { "name": "{分類}" } },
    "專長/工種": { "multi_select": [{ "name": "{工種1}" }, { "name": "{工種2}" }] },
    "往來狀態": { "status": { "name": "待聯繫" } },
    "配合評價": { "select": { "name": "未合作過" } },
    "服務區域": { "multi_select": [{ "name": "{區域}" }] },
    "備註": { "rich_text": [{ "type": "text", "text": { "content": "{備註}" } }] }
  }
}
```

記錄回傳的 `page_id`，供 STEP 6 更新名片檔案使用。

---

### STEP 5：複製名片照片到 Dropbox

1. 確認來源路徑（使用者提供的圖片路徑）
2. 新檔名格式：`YYYYMMDD-{姓名}-{公司簡稱}.{副檔名}`
   - 日期：今天日期
   - 公司簡稱：去掉「有限公司/股份有限公司/工程行」等後綴，保留前 4~6 字
   - 範例：`20260601-郭致廷-一昌冷凍空調.jpg`
3. 目標路徑：`/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/400_Knowledge/工程/客戶/名片/{新檔名}`
4. 使用 Bash `cp` 複製：

```bash
cp "{來源路徑}" "/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/400_Knowledge/工程/客戶/名片/{新檔名}"
```

---

### STEP 6：取得 Dropbox 分享連結並更新 Notion

使用 Node.js 取得分享連結（憑證從 `/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/.env` 讀取）：

```js
import('dotenv/config').then(async () => {
  const APP_KEY = 't1n8ea51gyluo9o';
  const SECRET = process.env.DROPBOX_APP_SECRET;
  const REFRESH = process.env.DROPBOX_REFRESH_TOKEN;

  const tokenResp = await fetch('https://api.dropboxapi.com/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: REFRESH, client_id: APP_KEY, client_secret: SECRET })
  });
  const { access_token: token } = await tokenResp.json();

  const FILE_PATH = '/Tu-agent/400_Knowledge/工程/客戶/名片/{新檔名}';
  const shareResp = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: FILE_PATH, settings: { requested_visibility: 'public' } })
  });
  const shareData = await shareResp.json();
  let shareUrl;
  if (shareData.url) {
    shareUrl = shareData.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '');
  } else if (shareData.error?.['.tag'] === 'shared_link_already_exists') {
    const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: FILE_PATH, direct_only: true })
    });
    const listData = await listResp.json();
    shareUrl = listData.links?.[0]?.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '');
  }
  console.log('URL:' + shareUrl);
});
```

取得 URL 後，使用 `mcp__notion__API-patch-page` 更新名片檔案欄位：

```json
{
  "page_id": "{STEP 4 的 page_id}",
  "properties": {
    "名片檔案": {
      "files": [{
        "type": "external",
        "name": "{新檔名}",
        "external": { "url": "{shareUrl}" }
      }]
    }
  }
}
```

---

### STEP 7：最終回報

```
✅ 名片建檔完成

👤 {姓名}（{職稱}）
🏢 {公司/單位}
📱 {手機}
📧 {Email}
🏷️ 分類：{分類} ／ 工種：{工種}
📎 名片照片：已歸檔至 Dropbox + 連結寫入 Notion

🔗 Notion 連結：{url}
```

---

## 重要規則

1. **STEP 1 確認後才繼續**，不自動全部執行
2. **查重不可跳過**，有相似記錄一定要告知使用者
3. **手機欄位格式**：直接填數字，如 `0933-522-556`
4. **名片照片一定要歸檔**，不留在 Downloads
5. **Obsidian vault 不建立客戶 .md 檔**，統一用 Notion 管理


---

## 分類

[[Skill目錄]]
