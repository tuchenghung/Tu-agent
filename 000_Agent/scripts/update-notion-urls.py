from dotenv import load_dotenv; load_dotenv()
import os
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['NOTION_TOKEN']

def to_url(path):
    return 'file:///' + path.replace('\\', '/').replace(' ', '%20')

def patch(page_id, props):
    data = json.dumps({'properties': props}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f'https://api.notion.com/v1/pages/{page_id}',
        data=data,
        headers={
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        },
        method='PATCH'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print('OK', page_id[:8])
    except urllib.error.HTTPError as e:
        print('ERR', e.read().decode('utf-8')[:300])

records = [
    (
        '36c7aebd-089f-811a-95bd-e844e8198bb4',
        r'D:\Dropbox\宏祐\規劃中案件\20260410羅東聖母8樓戒護病房整修工程\D預算報價\20260504-羅東聖母醫院S棟8樓戒護病房整修工程V4.xlsx',
        r'D:\Dropbox\宏祐\規劃中案件\20260410羅東聖母8樓戒護病房整修工程\K施工圖面\20260422-羅東聖母醫院S棟8樓監護病房整修工程T2.dwg'
    ),
    (
        '36c7aebd-089f-81a5-8868-ec545b5d8f87',
        r'D:\Dropbox\宏祐\施工中案件\20251104羅東聖母G棟中醫診所建置工程\D預算報價\20251014-羅東聖母醫院1F中醫診所報價V3.xlsx',
        r'D:\Dropbox\宏祐\施工中案件\20251104羅東聖母G棟中醫診所建置工程\K施工圖面\20260112-羅東聖母醫院1F中醫診所-T28.dwg'
    ),
    (
        '36c7aebd-089f-817b-bb91-f1c9bbd125b0',
        r'D:\Dropbox\宏祐\施工中案件\花蓮慈濟高劑量核種治療病房\預算報價\20240115-花慈核種治療病房及B2F核衰槽工程合約版-W0.xlsx',
        r'D:\Dropbox\宏祐\施工中案件\花蓮慈濟高劑量核種治療病房\圖面\竣工圖\20260325-花蓮慈濟高劑量核種治療病房工程.dwg'
    ),
]

for pid, quote_path, drawing_path in records:
    patch(pid, {
        '報價單路徑': {'url': to_url(quote_path)},
        '圖說路徑':   {'url': to_url(drawing_path)},
    })
