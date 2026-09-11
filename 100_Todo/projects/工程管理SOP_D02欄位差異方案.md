# D02 單價資料欄位差異與來源補齊方案

2026-09-10｜設計稿，供報價與查價工作台初版使用。依既有盤點文件整理，未重新查詢即時 Notion schema、未修改正式資料或進度主檔。以下「既有」是盤點已見，不代表已取得所有 property ID、實際型別或完成使用位置核對。

依據：[報價與單價資料規則](工程管理SOP_報價與單價資料規則.md)、[資料關聯盤點](工程管理SOP_資料關聯盤點.md)。

## 1. 欄位差異

| 資料責任 | 既有可沿用 | 建議新增／結構化 | 未核對與實體化前條件 |
|---|---|---|---|
| Projects 案件身分 | 頁面 ID、集團、公司別 | 工作台映射使用 projectId；公司受控映射另存 | 即時選項及公司別名對應；不得視名稱近似為同法人 |
| 供應商 | 頁面 ID、聯絡資料、工種、報價關聯 | 工作台使用 supplierId | 統編 number 另案核對原憑證，不在 D02 直接轉型補零 |
| 工程報價明細 | 品名、規格、單位、數量、單價、供應商、案件、文件、工種、日期、行情評估 | 文件版次 ID、原行識別、價格類型、幣別、稅基與稅率依據、原文、標準化單位、必要規格、包含／除外範圍、來源位置、可引用狀態 | 各欄精確名稱、property ID、型別、relation 目標與既有 Skill／網站依賴；日期語意是否報價日亦待核對 |
| 文件中心／版本 | 文件名稱、類別、系統時間與編輯者；報價庫已有文件關聯 | 每一實際版次保留文件 ID、報價識別、版次、雜湊、供應商、案件、報價日期、前版、原檔位置及分析狀態 | 盤點未見案件／版次／檔案路徑欄；可能存在正文，先查正文及 relation 目標，不能直接判遺失 |
| 單價分析 | 行情評估可保留原值 | 先在原价格頁固定正文存驗算、範圍、比較依據、差異、工料拆解狀態與待補事項 | 不將舊行情評估視為已完成分析；初版不新增平行分析資料庫 |
| 新案成本採用 | 兩份依據未證明既有採用表 | 隔離工作底稿保留目標案件／工項、來源快照、調整算式與依據、採用成本、核定資訊、Excel 映射 | 正式存放表與 B10 成本位置未確認前，只可預覽，不寫正式成本 |
| 重送／續跑紀錄 | 尚未證實已共用 | operationId、文件版次＋原行＋價格類型、步驟狀態、讀回結果 | 網站與 Skill 共用鎖未完成；這些欄位本身不構成交易保護 |

**採用方式：**先做工作台 JSON 邏輯欄位與既有欄位映射；取得即時 schema 和使用位置清單後，才逐欄決定 Notion property 或正文存放。保留原庫、不批次覆寫、不先複製全庫另建資料庫。原報價、成交價、分析估算、業主售價分開；無證據的舊資料價格類型維持 unknown。

## 2. 來源補齊優先序

既有查詢範圍為 2,105 筆，案件關聯空白 356、文件關聯空白 104、單價空白 2、單位空白 1；缺漏可能重疊，不能相加當問題筆數，亦不是本次即時重新統計。

| 優先序 | 範圍與行動 | 完成證據／未補齊處理 |
|---|---|---|
| P0 | 本次 B10／測試所選品項：確認來源案件 ID、供應商 ID、文件版次與原行 | 回到原文件頁碼或工作表／儲存格；案名歧義不得自動掛案。只有合成資料時明示 synthetic，不宣稱實檔驗收 |
| P1 | 優先處理本次候選中的缺文件關聯：先查價格頁正文，再查文件中心與原檔 | 補齊路徑及定位證據才列可追溯；找不到列待補，不刪除舊價 |
| P2 | 處理候選的缺案件關聯、单價或單位，以及稅基、規格、範圍、時點 | 對原文逐項確認；未知值保留 null，不當 0、不推定未稅、不把式換成面積單價 |
| P3 | 擴及高頻工種與近期會引用品項；逐筆記版次、價格類型、來源及可比差異 | 保留舊資料；引用資格逐筆判定，未採用不等於不可用、曾成交不等於新案可用 |
| P4 | 剩餘歷史資料依需求滾動補齊；再評估是否建工項規則表 | 留補齊批次、原值、證據與結果；不要求清完 2,105 筆才開始查價 |

每筆待補項目最少記 `recordId / field / currentValue / missingReason / evidenceChecked / nextAction / status`。缺文件但正文有原檔者，屬待補關聯，不能列原檔遺失。資料不足可顯示於待補清單，不能混入合格成本候選。

## 3. 初版工作台 JSON 契約

下列是欄位範本，所有 null 均表示未知或尚未提供；空清單不代表範圍已確認。ID 值需由實際來源取得，範本不可直接提交 Notion。

```json
{
  "schemaVersion": "0.1",
  "mode": "preview",
  "dataOrigin": "unverified",
  "operationId": null,
  "source": {
    "priceRecordId": null,
    "projectId": null,
    "group": null,
    "company": null,
    "supplierId": null,
    "documentId": null,
    "documentVersionId": null,
    "versionLabel": null,
    "previousVersionId": null,
    "filePath": null,
    "fileHash": null,
    "quoteDate": null,
    "validUntil": null,
    "lineId": null,
    "locator": {"page": null, "sheet": null, "cellRange": null}
  },
  "original": {
    "itemText": null,
    "specText": null,
    "rowType": "unknown",
    "quantity": null,
    "unit": null,
    "unitPrice": null,
    "lineAmount": null,
    "currency": null,
    "priceType": "unknown",
    "taxBasis": "unknown",
    "taxRate": null,
    "taxEvidence": null
  },
  "normalized": {
    "workType": null,
    "unit": null,
    "unitConversion": null,
    "specifications": {},
    "includedScope": [],
    "excludedScope": [],
    "scopeVerified": false,
    "siteConditions": null,
    "warranty": null
  },
  "analysis": {
    "status": "pending",
    "recalculatedAmount": null,
    "difference": null,
    "calculationEvidence": null,
    "breakdownStatus": "missing_evidence",
    "breakdown": [],
    "comparisonSources": [],
    "differences": [],
    "missingFields": [],
    "referenceStatus": "needs_information",
    "decisionReasons": []
  },
  "adoption": {
    "targetProjectId": null,
    "targetItemId": null,
    "targetQuantity": null,
    "sourceSnapshot": null,
    "adjustments": [],
    "adoptedUnitCost": null,
    "approvedBy": null,
    "approvedAt": null,
    "excelMapping": {"fileVersion": null, "sheet": null, "cell": null, "verified": false},
    "status": "draft"
  },
  "validation": {"errors": [], "warnings": [], "readbackVerified": false}
}
```

- `priceType`：`original_quote / agreed_price / analysis_estimate / owner_sale_price / unknown`，不可由採用狀態推定。
- `rowType`：至少區分 `item / subtotal / discount / tax / total / unquoted / unknown`，不把彙總列當單價候選。
- `referenceStatus`：`direct / adjusted / comparison_only / needs_information`。候選清單應明確區隔各級，`comparison_only`、`needs_information` 不可寫正式成本。
- `sourceSnapshot` 保存採用當時來源 ID、版次、原數值、單位、稅基、範圍與擷取時間，不能只留會變動的連結。
- `adjustments` 每項包含項目、原值、算式、結果、單位與依據；不設「一律加 10%」預設。金額計算需明示小數精度與捨入規則，不以浮點顯示值直接定案。
- 分析狀態、廠商採用狀態、引用資格是不同維度；廠商未採用原因不得自動生成。此範本不含正式記帳 API、售價填寫或發包動作。

## 4. 十項驗收邊界

| # | 測試情境 | 通過條件 |
|---|---|---|
| 1 | 同檔重送及逾時續跑 | 同版同原行不重複；按已完成步驟讀回後續作，不僅比較檔名 |
| 2 | 同廠同日新版及跨案同檔 | 新版不覆舊版；跨案來源情境分開，不因雜湊相同自動併案 |
| 3 | 缺單價／單位／案 ID／來源 | null 不作 0；缺口可查閱，不能標直接引用或正式完成 |
| 4 | 原複價錯誤及整包折讓 | 原值保留、差異另列；沒有逐項依據不攤造成交單價 |
| 5 | 同名不同規格、式對平方公尺 | 硬性条件未符即不自動匹配；不推算未知面積或以相似分數通過 |
| 6 | 稅別、日期、施工條件未明 | 列待核對理由；不預設未稅、半年失效或固定調價比例 |
| 7 | 連工帶料報價及三家僅選一家 | 三家逐項分析均保留；缺依據不編材料人工比例，入庫不自動發包 |
| 8 | 歷史價採用到新案 | 完整來源快照、調整依據和目標映射；不覆寫來源原價；售價由使用者核定 |
| 9 | B10 公共標單漏項與合包 | 原列及數量不改；漏報不作 0，合包總額不重複；實際成本區驗證前不可填表 |
| 10 | 宏祐／未知歸屬及測試版操作 | 可作報價分析參考；不產生 YUSHI 分錄；preview 不寫正式 Notion、原 Excel 或外部訊息 |

以上是待執行測試規格，並非已通過的實檔驗收結果。D02 正式完成仍需即時 schema 映射、既有呼叫依賴核對、來源補齊樣本讀回，以及 B10 副本端到端驗證。
