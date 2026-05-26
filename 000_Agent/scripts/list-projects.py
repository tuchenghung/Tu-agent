import os, sys
sys.stdout.reconfigure(encoding='utf-8')
base = r'D:\Dropbox\宏祐\規劃中案件'
for d in sorted(os.listdir(base)):
    print(d)
