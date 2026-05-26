import sys, pdfplumber
sys.stdout.reconfigure(encoding='utf-8')

files = {
    '第1包 結構補強': r'D:\Dropbox\宏祐\已完成案件\羅東聖母正子\B業主提供合同資料\定案版\一包結構補強工程\羅東聖母正子中心建置_第1包-結構補強工程 合約書正本.pdf',
    '第2包 屏蔽裝修': r'D:\Dropbox\宏祐\已完成案件\羅東聖母正子\B業主提供合同資料\定案版\二包屏蔽裝修工程\羅東聖母正子中心建置_第2包-屏蔽裝修工程合約書正本.pdf',
    '第3包 核衰設備': r'D:\Dropbox\宏祐\已完成案件\羅東聖母正子\B業主提供合同資料\定案版\三包核衰設備採購\S113102401 羅東聖母-正子中心輻射污水(18FDG_Lu177)核衰設備採購案.pdf',
}

for name, path in files.items():
    print(f'\n{"="*60}')
    print(f'【{name}】')
    print(f'{"="*60}')
    try:
        with pdfplumber.open(path) as pdf:
            print(f'共 {len(pdf.pages)} 頁')
            # 讀前6頁
            for i, page in enumerate(pdf.pages[:6]):
                text = page.extract_text()
                if text:
                    print(f'\n--- 第{i+1}頁 ---')
                    print(text[:2000])
    except Exception as e:
        print(f'錯誤: {e}')
