from dotenv import load_dotenv; load_dotenv()
import os
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['NOTION_TOKEN']
DB_ID = '36c7aebd-089f-81f2-adfc-e984d65b4bbd'

QUOTE = r'D:\Dropbox\宏祐\舊案件\羅東聖母醫院南澳日照中心\D預算報價\20250818南澳工成報價單.xlsx'
DWG   = r'D:\Dropbox\宏祐\舊案件\羅東聖母醫院南澳日照中心\A業主提供資料\院方提供圖檔\1140801.dwg'

def to_url(path):
    return 'file:///' + path.replace('\\', '/').replace(' ', '%20')

def api(method, url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data,
        headers={'Authorization': f'Bearer {TOKEN}',
                 'Content-Type': 'application/json',
                 'Notion-Version': '2022-06-28'},
        method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode('utf-8')[:400]

# 新增 工程類別 選項
_, err = api('PATCH', f'https://api.notion.com/v1/databases/{DB_ID}', {
    'properties': {
        '工程類別': {'select': {'options': [
            {'name': '病房整修',    'color': 'purple'},
            {'name': '門診整修',    'color': 'pink'},
            {'name': '手術室',      'color': 'red'},
            {'name': 'ICU/護理站',  'color': 'orange'},
            {'name': '建置工程',    'color': 'blue'},
            {'name': '社福機構新建','color': 'yellow'},
            {'name': '其他',        'color': 'gray'},
        ]}}
    }
})
print('DB schema:', 'OK' if not err else err)

# 新增記錄
r, err = api('POST', 'https://api.notion.com/v1/pages', {
    'parent': {'database_id': DB_ID},
    'properties': {
        '案件名稱':   {'title': [{'text': {'content': '羅東聖母醫院南澳日照中心新建工程'}}]},
        '業主':       {'rich_text': [{'text': {'content': '天主教靈醫會醫療財團法人羅東聖母醫院'}}]},
        '工程類型':   {'select': {'name': '私人醫院'}},
        '工程類別':   {'select': {'name': '社福機構新建'}},
        '總金額_報價':{'number': 24975876},
        '毛利率':     {'number': 0.05},
        '空間坪數':   {'number': 66},
        '每坪單價':   {'number': 378422},
        '報價日期':   {'date': {'start': '2025-08-18'}},
        '狀態':       {'select': {'name': '規劃中'}},
        '報價單路徑': {'url': to_url(QUOTE)},
        '圖說路徑':   {'url': to_url(DWG)},
        '備注':       {'rich_text': [{'text': {'content':
            '日照中心新建工程/H型鋼結構45T+RC基礎/屋頂鈦鋁板/40HP水冷式空調/20人份污水處理/含戶外景觀/利潤5%+稅5%/舊案件'
        }}]},
    }
})
print('Record:', r.get('id') if r else err)
