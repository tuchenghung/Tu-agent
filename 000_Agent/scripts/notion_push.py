import urllib.request, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = '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'
DB_ID = '1e25b3e6-e630-4f67-8677-f97a9a8dd159'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
LOCAL_DIR = r'D:\Dropbox\Tu-agent\400_Knowledge\工程\建材規格'

def api(method, path, body=None):
    url = f'https://api.notion.com/v1{path}'
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def clean(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text.strip()

def md_to_blocks(content, local_path, local_fname):
    blocks = []
    safe_path = local_path.replace('\\', '/').replace(' ', '%20')
    file_url = 'file:///' + safe_path
    blocks.append({
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": "📁 本機路徑："},
                 "annotations": {"bold": True}},
                {"type": "text", "text": {"content": "400_Knowledge/工程/建材規格/" + local_fname},
                 "annotations": {"code": True}}
            ]
        }
    })

    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    lines = content.split('\n')
    table_noted = False

    for line in lines:
        s = line.strip()
        if not s or s == '---':
            continue
        if s.startswith('# ') and not s.startswith('## '):
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": s[2:500]}}]}})
        elif s.startswith('## '):
            table_noted = False
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": s[3:500]}}]}})
        elif s.startswith('### '):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": s[4:500]}}]}})
        elif s.startswith('|'):
            if not table_noted and '---' not in s:
                blocks.append({"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "（詳細規格表格請開本機 .md 檔案）"}, "annotations": {"italic": True, "color": "gray"}}]}})
                table_noted = True
        elif s.startswith('- ') or s.startswith('* '):
            t = clean(s[2:])
            if len(t) > 1:
                blocks.append({"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t[:500]}}]}})
        elif re.match(r'^\d+\.\s', s):
            t = clean(re.sub(r'^\d+\.\s', '', s))
            blocks.append({"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": t[:500]}}]}})
        elif len(s) > 3:
            t = clean(s)
            if len(t) > 3:
                blocks.append({"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": t[:2000]}}]}})

    return blocks[:100]

# 取 Notion 頁面
pages_data = api('POST', f'/databases/{DB_ID}/query', {"page_size": 100})
notion_map = {}
for p in pages_data['results']:
    for key, prop in p['properties'].items():
        if prop['type'] == 'title':
            title = ''.join([t['plain_text'] for t in prop['title']])
            notion_map[title] = p['id']
            break

skip_titles = {
    '菲米諾立體切邊吸音板 — 選用指南與工法',
    '(廣華) 興業KOWA FFU 2×2｜420 CMH｜',
    '南港實驗室 乾盤管圖面－嘉祿（DC-1150428）',
    'AC1700 粉塵淨化機',
    '戒護病房設置規定（醫療機構設置標準修正要點）',
    '玻纖防火門、金屬防火門、木質防火門比價差異及價格',
    '防火門採購必看：揭開價格背後的 5 個隱藏真相',
    '窗戶挑選指南：uPVC 與斷橋鋁窗的深度對決',
    'XLPE 延燃電纜 vs XLPE 電纜（差異）',
    '惰性氣體滅火設備 潔淨氣體滅火設備 差異GPT查詢',
}

local_files = [f for f in os.listdir(LOCAL_DIR) if f.endswith('.md') and '.tmp.' not in f]
updated = 0
skipped = 0

for fname in sorted(local_files):
    filepath = os.path.join(LOCAL_DIR, fname)
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    fm_title = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
    md_title = (fm_title.group(1).strip() if fm_title else
                title_match.group(1).strip() if title_match else '')

    page_id = None
    for n_title, pid in notion_map.items():
        if n_title in skip_titles:
            continue
        if md_title and (md_title[:25] in n_title or n_title[:25] in md_title):
            page_id = pid
            break

    if not page_id:
        print(f'no match: {fname[:60]}')
        skipped += 1
        continue

    existing = api('GET', f'/blocks/{page_id}/children?page_size=3')
    if len(existing.get('results', [])) > 0:
        print(f'skip (has content): {fname[:50]}')
        skipped += 1
        continue

    blocks = md_to_blocks(content, filepath, fname)
    try:
        api('PATCH', f'/blocks/{page_id}/children', {"children": blocks})
        print(f'OK  {fname[:65]}')
        updated += 1
    except Exception as e:
        print(f'ERR {fname[:50]} {str(e)[:80]}')

print(f'\ndone: updated={updated} skipped={skipped}')
