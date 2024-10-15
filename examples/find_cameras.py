import cv2

def find_available_cameras():
    index = 0
    available_cameras = []
    
    while True:
        # 嘗試打開相機設備
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # 使用 DirectShow 打開相機
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
        else:
            break  # 遇到無法打開的相機時停止
        index += 1
    
    return available_cameras

# 列出所有可用的相機
cameras = find_available_cameras()

if cameras:
    print(f"找到 {len(cameras)} 台可用的相機。相機編號：{cameras}")
else:
    print("沒有可用的相機。")
