import win32com.client

try:
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    doc = acad.ActiveDocument

    print("=== 檔案資訊 ===")
    print("檔案名稱:", doc.Name)
    print("檔案路徑:", doc.FullName)

    print("\n=== 圖層清單 ===")
    layers = doc.Layers
    for i in range(layers.Count):
        layer = layers.Item(i)
        status = "開啟" if layer.LayerOn else "關閉"
        frozen = "凍結" if layer.Freeze else "正常"
        print(f"  - {layer.Name} | {status} | {frozen} | 顏色:{layer.color}")

    print("\n=== 圖塊清單 ===")
    blocks = doc.Blocks
    for i in range(blocks.Count):
        blk = blocks.Item(i)
        if not blk.Name.startswith("*"):
            print(f"  - {blk.Name} | 物件數:{blk.Count}")

    print("\n=== 基本統計 ===")
    ms = doc.ModelSpace
    print("模型空間物件總數:", ms.Count)

except Exception as e:
    print("錯誤:", e)
    print("請確認 AutoCAD 已開啟且有開啟檔案")
